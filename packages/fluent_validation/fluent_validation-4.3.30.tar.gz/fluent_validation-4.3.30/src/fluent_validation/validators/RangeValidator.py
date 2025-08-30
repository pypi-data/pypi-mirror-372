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
from abc import abstractmethod
from typing import override, TYPE_CHECKING

from fluent_validation.validators.ComparableComparer import IComparer

if TYPE_CHECKING:
    from fluent_validation.validators.ExclusiveBetweenValidator import ExclusiveBetweenValidator
    from fluent_validation.validators.InclusiveBetweenValidator import InclusiveBetweenValidator
from fluent_validation.IValidationContext import ValidationContext

from fluent_validation.validators.PropertyValidator import PropertyValidator
from fluent_validation.validators.IpropertyValidator import IPropertyValidator


class IBetweenValidator(IPropertyValidator):
    From: object
    To: object


class RangeValidator[T, TProperty](PropertyValidator[T, TProperty], IBetweenValidator):
    def __init__(self, ini: TProperty, to: TProperty, comparer: IComparer[TProperty]):
        self._to: TProperty = to
        self._from: TProperty = ini

        self._explicitComparer: IComparer[TProperty] = comparer

        if comparer.Compare(to, ini) == -1:
            raise IndexError(f"'{self._to} To should be larger than from.")

    @property
    def From(self):
        return self._from

    @property
    def To(self):
        return self._to

    @abstractmethod
    def HasError(self, value: TProperty) -> bool: ...

    @override
    def is_valid(self, context: ValidationContext[T], value: TProperty):
        # If the value is null then we abort and assume success.
        # This should not be a failure condition - only a not_null/not_empty should cause a null to fail.
        if value is None:
            return True

        if self.HasError(value):
            context.MessageFormatter.AppendArgument("From", self.From)
            context.MessageFormatter.AppendArgument("To", self.To)
            return False

        return True

    def Compare(self, a: TProperty, b: TProperty) -> int:
        return self._explicitComparer.Compare(a, b)

    @override
    def get_default_message_template(self, errorCode: str) -> str:
        return self.Localized(errorCode, self.Name)


class RangeValidatorFactory:
    @staticmethod
    def CreateExclusiveBetween[T, TProperty](from_: TProperty, to: TProperty) -> ExclusiveBetweenValidator[T, TProperty]:
        from fluent_validation.validators.ExclusiveBetweenValidator import ExclusiveBetweenValidator
        from .ComparableComparer import ComparableComparer

        return ExclusiveBetweenValidator[T, TProperty](from_, to, ComparableComparer[TProperty])

    @staticmethod
    def CreateInclusiveBetween[T, TProperty](from_: TProperty, to: TProperty) -> InclusiveBetweenValidator[T, TProperty]:
        from fluent_validation.validators.InclusiveBetweenValidator import InclusiveBetweenValidator
        from .ComparableComparer import ComparableComparer

        return InclusiveBetweenValidator[T, TProperty](from_, to, ComparableComparer[TProperty])
