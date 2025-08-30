# region License
# Copyright (c) .NET Foundation and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The latest version of this file can be found at https://github.com/p-hzamora/FluentValidation
# endregion

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Type, overload

from fluent_validation.DefaultValidatorExtensions_Validate import DefaultValidatorExtensions_Validate

if TYPE_CHECKING:
    from fluent_validation.internal.ValidationStrategy import ValidationStrategy
    from fluent_validation.IValidationContext import IValidationContext
    from .results.ValidationResult import ValidationResult


class IValidator_no_generic(ABC):
    @abstractmethod
    def validate(self, context: IValidationContext) -> ValidationResult: ...

    @abstractmethod
    async def ValidateAsync(self, context: IValidationContext) -> ValidationResult: ...  # CancellationToken cancellation = new CancellationToken()

    # @abstractmethod
    # def CreateDescriptor(self,)->IValidatorDescriptor: ...

    @abstractmethod
    def CanValidateInstancesOfType(type: Type) -> bool: ...


class IValidator[T](IValidator_no_generic, DefaultValidatorExtensions_Validate):
    @overload
    def validate(validator: IValidator[T], instance: T) -> ValidationResult: ...

    @overload
    def validate(validator: IValidator[T], instance: IValidationContext) -> ValidationResult: ...

    @overload
    def validate(validator: IValidator[T], instance: T, options: Callable[[ValidationStrategy[T]], None]) -> ValidationResult: ...

    @abstractmethod
    def validate(validator, instance, options): ...

    # TODOL: Checked in C#
    @abstractmethod
    async def ValidateAsync(validator: IValidator[T], instance: T) -> ValidationResult: ...  # CancellationToken cancellation = new CancellationToken()
