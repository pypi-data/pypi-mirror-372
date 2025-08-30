# Copyright 2022, The TensorFlow Federated Authors.
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
# See the License for the specific language governing permissions and
# limitations under the License.
"""A federated platform implemented using native components."""

import asyncio
from collections.abc import Mapping
from typing import Optional, Union

from federated_language.common_libs import structure
from federated_language.computation import computation_base
from federated_language.context_stack import context
from federated_language.program import federated_context
from federated_language.program import structure_utils
from federated_language.program import value_reference
from federated_language.types import computation_types
from federated_language.types import placements
from federated_language.types import type_conversions
import tree


class NativeValueReference(value_reference.MaterializableValueReference):
  """A `federated_language.program.MaterializableValueReference` backed by a task."""

  def __init__(
      self,
      task: asyncio.Task,
      type_signature: value_reference.MaterializableTypeSignature,
  ):
    """Returns an initialized `federated_language.program.NativeValueReference`.

    Args:
      task: An `asyncio.Task` to run.
      type_signature: The `federated_language.Type` of this object.
    """
    self._task = task
    self._type_signature = type_signature

  @property
  def type_signature(
      self,
  ) -> value_reference.MaterializableTypeSignature:
    """The `federated_language.TensorType` of this object."""
    return self._type_signature

  async def get_value(self) -> value_reference.MaterializedValue:
    """Returns the referenced value as a numpy scalar or array."""
    return await self._task

  def __eq__(self, other: object) -> bool:
    if self is other:
      return True
    elif not isinstance(other, NativeValueReference):
      return NotImplemented
    return (
        self._type_signature,
        self._task,
    ) == (
        other._type_signature,
        other._task,
    )


def _create_structure_of_references(
    task: asyncio.Task,
    type_signature: computation_types.Type,
) -> structure_utils.Structure[NativeValueReference]:
  """Returns a structure of `federated_language.program.NativeValueReference`s.

  Args:
    task: A task used to create the structure of
      `federated_language.program.NativeValueReference`s.
    type_signature: The `federated_language.Type` of the value returned by
      `task`; must contain only structures, server-placed values, or tensors.

  Raises:
    NotImplementedError: If `type_signature` contains an unexpected type.
  """
  if isinstance(type_signature, computation_types.StructType):

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

    async def _get_item(
        task: asyncio.Task, key: Union[str, int]
    ) -> value_reference.MaterializedValue:
      value = await task
      return value[key]

    elements = []
    for index, (name, element_type) in enumerate(type_signature.items()):
      container_cls = _get_container_cls(type_signature)
      if issubclass(container_cls, Mapping):
        key = name
      else:
        key = index
      element = _get_item(task, key)
      element_task = asyncio.create_task(element)
      element = _create_structure_of_references(element_task, element_type)
      elements.append(element)
    return type_conversions.to_structure_with_type(elements, type_signature)
  elif (
      isinstance(type_signature, computation_types.FederatedType)
      and type_signature.placement == placements.SERVER
  ):
    return _create_structure_of_references(task, type_signature.member)
  elif isinstance(type_signature, computation_types.SequenceType):
    return NativeValueReference(task, type_signature)
  elif isinstance(type_signature, computation_types.TensorType):
    return NativeValueReference(task, type_signature)
  else:
    raise NotImplementedError(f'Unexpected type found: {type_signature}.')


class NativeFederatedContext(federated_context.FederatedContext):
  """A `federated_language.program.FederatedContext` backed by a context."""

  def __init__(self, ctx: context.AsyncContext):
    """Returns an initialized `federated_language.program.NativeFederatedContext`.

    Args:
      ctx: An `federated_language.framework.AsyncContext`.
    """
    self._ctx = ctx

  def invoke(
      self,
      comp: computation_base.Computation,
      arg: Optional[federated_context.ComputationArg],
  ) -> structure_utils.Structure[NativeValueReference]:
    """Invokes the `comp` with the argument `arg`.

    Args:
      comp: The `federated_language.Computation` being invoked.
      arg: The optional argument of `comp`; server-placed values must be
        represented by `federated_language.program.MaterializableStructure`, and
        client-placed values must be represented by structures of values
        returned by a `federated_language.program.FederatedDataSourceIterator`.

    Returns:
      The result of invocation; a structure of
      `federated_language.program.MaterializableValueReference`.

    Raises:
      ValueError: If the result type of the invoked computation does not contain
      only structures, server-placed values, or tensors.
    Raises:
      ValueError: If the result type of `comp` does not contain only structures,
      server-placed values, or tensors.
    """
    result_type = comp.type_signature.result
    if not federated_context.contains_only_server_placed_data(result_type):
      raise ValueError(
          'Expected the result type of `comp` to contain only structures, '
          f'server-placed values, or tensors, found {result_type}.'
      )

    async def _invoke(
        ctx: context.AsyncContext,
        comp: computation_base.Computation,
        arg: value_reference.MaterializableStructure,
    ) -> value_reference.MaterializedStructure:
      if comp.type_signature.parameter is not None:

        def _to_python(obj):
          if isinstance(obj, structure.Struct):
            return structure.to_odict_or_tuple(obj)
          else:
            return None

        arg = tree.traverse(_to_python, arg)
        arg = await value_reference.materialize_value(arg)

      return await ctx.invoke(comp, arg)

    coro = _invoke(self._ctx, comp, arg)
    task = asyncio.create_task(coro)
    return _create_structure_of_references(task, result_type)
