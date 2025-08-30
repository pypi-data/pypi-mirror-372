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

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, override

from fluent_validation.IValidationContext import ValidationContext
from fluent_validation.MemberInfo import MemberInfo
from fluent_validation.validators.PropertyValidator import PropertyValidator
from fluent_validation.validators.AbstractComparisonValidator import Comparison, IComparisonValidator


class IEqualValidator(IComparisonValidator): ...


class IEqualityComparer[T](ABC):
    @abstractmethod
    def Equals(x: Optional[T], y: Optional[T]): ...


class EqualValidator[T, TProperty](PropertyValidator[T, TProperty], IEqualValidator):
    def __init__(
        self,
        valueToCompare: TProperty = None,
        comparer: IEqualityComparer[TProperty] = None,
        comparisonProperty: Callable[[T], TProperty] = None,
        member: MemberInfo = None,
        memberDisplayName: str = None,
    ):
        self._func = comparisonProperty
        self._memberDisplayName = memberDisplayName
        self._MemberToCompare: MemberInfo = member
        self._ValueToCompare = valueToCompare
        self._comparer = comparer

    def is_valid(self, context: ValidationContext[T], value: TProperty) -> bool:
        comparisonValue = self.GetComparisonValue(context)
        success: bool = self.Compare(comparisonValue, value)

        if not success:
            context.MessageFormatter.AppendArgument("ComparisonValue", comparisonValue)
            context.MessageFormatter.AppendArgument("ComparisonProperty", self._memberDisplayName if self._memberDisplayName else "")

            return False

        return True

    def GetComparisonValue(self, context: ValidationContext[T]) -> TProperty:
        if self._func is not None:
            return self._func(context.instance_to_validate)

        return self.ValueToCompare

    @override
    @property
    def ValueToCompare(self) -> Any:
        return self._ValueToCompare

    @override
    @property
    def MemberToCompare(self) -> MemberInfo:
        return self._MemberToCompare

    @override
    @property
    def Comparison(self) -> Comparison:
        return Comparison.equal

    def Compare(self, comparisonValue: TProperty, propertyValue: TProperty) -> bool:
        if self._comparer is not None:
            return self._comparer(comparisonValue, propertyValue)
        # TODOL: Checked if Equals method it's similar to '__eq__'
        return comparisonValue == propertyValue  # self.Equals(comparisonValue, propertyValue)

    @override
    def get_default_message_template(self, error_code: str) -> str:
        return self.Localized(error_code, self.Name)
