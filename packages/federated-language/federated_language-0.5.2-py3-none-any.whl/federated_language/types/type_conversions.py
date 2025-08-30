# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# limitations under the License.
"""Utilities for type conversion, type checking, type inference, etc."""

import collections
from collections.abc import Hashable, Mapping, Sequence
import functools
import typing
from typing import Optional, Union

import attrs
from federated_language.common_libs import py_typecheck
from federated_language.common_libs import structure
from federated_language.types import computation_types
from federated_language.types import dtype_utils
from federated_language.types import typed_object
import numpy as np
import tree


def infer_type(arg: object) -> Optional[computation_types.Type]:
  """Infers the type of the argument (a `computation_types.Type` instance).

  WARNING: This function is only partially implemented.

  The kinds of arguments that are currently correctly recognized:
  * tensors, variables, and data sets
  * things that are convertible to tensors (including `numpy` arrays, builtin
    types, as well as `list`s and `tuple`s of any of the above, etc.)
  * nested lists, `tuple`s, `namedtuple`s, anonymous `tuple`s, `dict`,
    `OrderedDict`s, `attrs` classes, and `federated_language.TypedObject`s

  Args:
    arg: The argument, the type of which to infer.

  Returns:
    Either an instance of `computation_types.Type`, or `None` if the argument is
    `None`.
  """

  # TODO: b/224484886 - Downcasting to all handled types.
  arg = typing.cast(
      Union[
          None,
          typed_object.TypedObject,
          py_typecheck.SupportsNamedTuple,
          Mapping[Hashable, object],
          tuple[object, ...],
          list[object],
      ],
      arg,
  )
  if arg is None:
    return None
  elif isinstance(arg, typed_object.TypedObject):
    return arg.type_signature
  elif attrs.has(type(arg)):
    items = attrs.asdict(arg, recurse=False).items()
    return computation_types.StructWithPythonType(
        [(k, infer_type(v)) for k, v in items], type(arg)
    )
  elif isinstance(arg, py_typecheck.SupportsNamedTuple):
    items = arg._asdict().items()
    return computation_types.StructWithPythonType(
        [(k, infer_type(v)) for k, v in items], type(arg)
    )
  elif isinstance(arg, Mapping):
    items = arg.items()
    return computation_types.StructWithPythonType(
        [(k, infer_type(v)) for k, v in items], type(arg)
    )
  elif isinstance(arg, (tuple, list)):
    elements = []
    all_elements_named = True
    for element in arg:
      all_elements_named &= py_typecheck.is_name_value_pair(
          element, name_type=str
      )
      elements.append(infer_type(element))
    # If this is a tuple of (name, value) pairs, the caller most likely intended
    # this to be a StructType, so we avoid storing the Python container.
    if elements and all_elements_named:
      return computation_types.StructType(elements)
    else:
      return computation_types.StructWithPythonType(elements, type(arg))
  elif isinstance(arg, (np.generic, np.ndarray)):
    return computation_types.TensorType(arg.dtype, arg.shape)
  elif isinstance(arg, (bool, int, float, complex, str, bytes)):
    dtype = dtype_utils.infer_dtype(arg)
    return computation_types.TensorType(dtype)
  else:
    raise NotImplementedError(f'Unexpected arg found: {type(arg)}.')


def to_structure_with_type(
    obj: object, type_spec: computation_types.Type
) -> object:
  """Converts the containers in `obj` to those defined by `type_spec`.

  NOTE: This function does not convert any leaf in the structure.

  For example:

  >>> obj = 1
  >>> type_spec = federated_language.TensorType(np.int32)
  >>> federated_language.types.to_structure_with_type(obj, type_spec)
  1

  >>> obj = [1, 2, 3]
  >>> type_spec = federated_language.StructType([np.int32] * 3)
  >>> federated_language.types.to_structure_with_type(obj, type_spec)
  [1, 2, 3]

  >>> obj = [1, 2, 3]
  >>> type_spec = federated_language.StructType([
  >>>     ('a', np.int32),
  >>>     ('b', np.int32),
  >>>     ('c', np.int32),
  >>> ])
  >>> federated_language.types.to_structure_with_type(obj, type_spec)
  {'a': 1, 'b': 2, 'c': 3}

  Args:
    obj: A Python value.
    type_spec: The `federated_language.Type` to use convert `obj`.

  Returns:
    A Python value equivalent to `obj` with a structure matching `type_spec`.

  Raises:
    ValueError: If `obj` and `type_spec` do not match or a container does not
      have either all named or unnamed elements.
  """

  def _get_item(
      type_spec: computation_types.Type, key: Union[str, int]
  ) -> Union[computation_types.FederatedType, computation_types.StructType]:
    if isinstance(type_spec, computation_types.FederatedType):
      if not type_spec.all_equal:
        return type_spec.member
      else:
        type_spec = type_spec.member
    elif isinstance(type_spec, computation_types.SequenceType):
      return type_spec.element

    if isinstance(type_spec, computation_types.StructType):
      return type_spec[key]
    else:
      raise ValueError(
          'Expected `type_spec` to be a `federated_language.StructType`, found'
          f' {type(type_spec)}.'
      )

  def _get_container_cls(
      type_spec: computation_types.StructType,
  ) -> type[object]:
    container_cls = type_spec.python_container
    if container_cls is None:
      has_names = [name is not None for name, _ in type_spec.items()]
      if any(has_names):
        if not all(has_names):
          raise ValueError(
              'Expected `type_spec` to have either all named or unnamed'
              f' elements, found {type_spec}.'
          )
        container_cls = dict
      else:
        container_cls = list
    return container_cls

  def _get_container_spec(
      type_spec: computation_types.Type,
  ) -> tuple[type[object], Optional[list[Optional[str]]]]:
    if isinstance(type_spec, computation_types.FederatedType):
      if not type_spec.all_equal:
        return list, None
      else:
        type_spec = type_spec.member
    elif isinstance(type_spec, computation_types.SequenceType):
      return list, None

    if isinstance(type_spec, computation_types.StructType):
      names = [name for name, _ in type_spec.items()]
      container_cls = _get_container_cls(type_spec)
      return container_cls, names
    else:
      raise ValueError(
          'Expected `type_spec` to be a `federated_language.StructType`,'
          ' found {type(type_spec)}.'
      )

  def _to_structure(path: tuple[Union[str, int], ...], obj: object) -> object:

    if tree.is_nested(obj):
      container_type = functools.reduce(_get_item, path, type_spec)
      container_cls, names = _get_container_spec(container_type)

      if isinstance(obj, py_typecheck.SupportsNamedTuple):
        elements = obj._asdict().values()
      elif isinstance(obj, Mapping):
        elements = obj.values()
      elif isinstance(obj, Sequence):
        elements = obj
      else:
        raise ValueError(
            'Expected `obj` to be a `NamedTuple`, `Mapping`, or `Sequence`,'
            f' found {type(obj)}.'
        )

      if isinstance(container_cls, py_typecheck.SupportsNamedTuple):
        return container_cls(**dict(zip(names, elements)))
      elif issubclass(container_cls, Mapping):
        return container_cls(zip(names, elements))  # pylint: disable=too-many-function-args
      elif issubclass(container_cls, Sequence):
        return container_cls(elements)  # pylint: disable=too-many-function-args
      else:
        raise ValueError(
            'Expected `container_cls` to be a `NamedTuple`, `Mapping`, or'
            f' `Sequence`, found {container_cls}.'
        )
    else:
      return None

  if tree.is_nested(obj):
    return tree.traverse_with_path(_to_structure, obj, top_down=False)
  else:
    return obj


def _is_container_type_without_names(container_type: type[object]) -> bool:
  """Returns whether `container_type`'s elements are unnamed."""
  return issubclass(container_type, (list, tuple)) and not isinstance(
      container_type, py_typecheck.SupportsNamedTuple
  )


def _is_container_type_with_names(container_type: type[object]) -> bool:
  """Returns whether `container_type`'s elements are named."""
  return (
      isinstance(container_type, py_typecheck.SupportsNamedTuple)
      or attrs.has(container_type)
      or issubclass(container_type, dict)
  )


def type_to_py_container(value, type_spec: computation_types.Type):
  """Recursively convert `structure.Struct`s to Python containers.

  This is in some sense the inverse operation to
  `structure.from_container`.

  This function assumes some unique behavior with regards to
  `federated_language.SequenceType`.
  If the `value` is a list, it may yield other `federated_language.StructTypes`
  as well as
  Python types. Otherwise, it may only yield Python types.

  Args:
    value: A structure of anonymous tuples of values corresponding to
      `type_spec`.
    type_spec: The `federated_language.Type` to which value should conform,
      possibly including `computation_types.StructWithPythonType`.

  Returns:
    The input value, with containers converted to appropriate Python
    containers as specified by the `type_spec`.

  Raises:
    ValueError: If the conversion is not possible due to a mix of named
      and unnamed values, or if `value` contains names that are mismatched or
      not present in the corresponding index of `type_spec`.
  """
  if isinstance(type_spec, computation_types.FederatedType):
    if type_spec.all_equal:
      structure_type_spec = type_spec.member
    else:
      if not isinstance(value, list):
        raise TypeError(
            'Unexpected Python type for non-all-equal type '
            f'{type_spec}: expected `list`, found `{type(value)}`.'
        )
      return [
          type_to_py_container(element, type_spec.member) for element in value
      ]
  else:
    structure_type_spec = type_spec

  if isinstance(structure_type_spec, computation_types.SequenceType):
    element_type = structure_type_spec.element
    if isinstance(value, list):
      return [type_to_py_container(element, element_type) for element in value]
    else:
      # Assume that the type of value does not understand `Struct` and that the
      # value must yield Python containers.
      return value

  if not isinstance(structure_type_spec, computation_types.StructType):
    return value

  if not isinstance(value, structure.Struct):
    # NOTE: When encountering non-`structure.Struct`s, we assume that
    # this means that we're attempting to re-convert a value that
    # already has the proper containers, and we short-circuit to
    # avoid re-converting. This is a possibly dangerous assumption.
    return value

  container_type = structure_type_spec.python_container

  # Ensure that names are only added, not mismatched or removed
  names_from_value = structure.name_list_with_nones(value)
  names_from_type_spec = structure.name_list_with_nones(structure_type_spec)
  for value_name, type_name in zip(names_from_value, names_from_type_spec):
    if value_name is not None:
      if value_name != type_name:
        raise ValueError(
            f'Cannot convert value with field name `{value_name}` into a '
            f'type with field name `{type_name}`.'
        )

  num_named_elements = len(dir(structure_type_spec))
  num_unnamed_elements = len(structure_type_spec) - num_named_elements
  if num_named_elements > 0 and num_unnamed_elements > 0:
    raise ValueError(
        f'Cannot represent value {value} with a Python container because it'
        ' contains a mix of named and unnamed elements.\n\nNOTE: this was'
        ' previously allowed when using the'
        ' `federated_language.structure.Struct` container. This support has'
        ' been removed: please change to use structures with either all-named'
        ' or all-unnamed fields.'
    )
  if container_type is None:
    if num_named_elements:
      container_type = collections.OrderedDict
    else:
      container_type = tuple

  # Avoid projecting the `structure.StructType`d value into a Python
  # container that is not supported.
  if num_named_elements > 0 and _is_container_type_without_names(
      container_type
  ):
    raise ValueError(
        'Cannot represent value {} with named elements '
        'using container type {} which does not support names. In the '
        'typesystem, this corresponds to an implicit downcast'.format(
            value, container_type
        )
    )
  if _is_container_type_with_names(container_type) and len(
      dir(structure_type_spec)
  ) != len(value):
    # If the type specifies the names, we have all the information we need.
    # Otherwise we must raise here.
    raise ValueError(
        'When packaging as a Python value which requires names, '
        'the type spec must have all names specified. Found '
        '{} names in type spec {} of length {}, with requested'
        'python type {}.'.format(
            len(dir(structure_type_spec)),
            structure_type_spec,
            len(value),
            container_type,
        )
    )

  elements = []
  for index, (elem_name, elem_type) in enumerate(structure_type_spec.items()):
    element = type_to_py_container(value[index], elem_type)

    if elem_name is None:
      elements.append(element)
    else:
      elements.append((elem_name, element))

  if isinstance(container_type, py_typecheck.SupportsNamedTuple) or attrs.has(
      container_type
  ):
    # The namedtuple and attr.s class constructors cannot interpret a list of
    # (name, value) tuples; instead call constructor using kwargs. Note that
    # these classes already define an order of names internally, so order does
    # not matter.
    return container_type(**dict(elements))
  else:
    # E.g., tuple and list when elements only has values, but also `dict`,
    # `collections.OrderedDict`, or `structure.Struct` when
    # elements has (name, value) tuples.
    return container_type(elements)  # pytype: disable=wrong-arg-count
