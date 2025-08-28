# -*- coding: utf-8 -*-

# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Provides a common base class for rules, with additional services.

This class stubs the original ``Rule`` class for unit tests.
"""

from typing import Dict, List, Optional

import scade.model.suite as suite

try:
    # ignore F401: _register_rule made available for rules, not used here
    # _register_rule is defined dynamically: ignore linter warning
    from scade.tool.suite import _register_rule  # noqa: F401  # type: ignore

    # _Rule defined hereafter is a stub, and thus can't match Rule
    from scade.tool.suite.rules import Rule as _Rule  # type: ignore
except ImportError:
    from .metric import Metric

    class _Rule:
        """Stubs ``Rule`` for units tests."""

        def __init__(self, *args, **kwargs):
            self.message = ''
            self.metrics = {}

        def set_message(self, message: str) -> None:
            """Store the message."""
            self.message = message

        def add_rule_status(
            self,
            object_: suite.Object,
            status: int,
            message: str,
            local_id: str = '',
        ) -> None:
            """Stub the ``add_rule_status`` method."""
            pass

        def stub_metrics(self, metrics: Dict[str, Metric]):
            """
            Store the metric instances for the evaluation.

            This method allows emulating the environment for unit tests.
            """
            self.metrics = metrics

        def get_metric_result(self, object_: suite.Object, metric_id: str) -> int:
            """
            Compute the value of a metric for an object.

            This method allows emulating the environment for unit tests.
            """
            metric = self.metrics[metric_id]
            status = metric.on_compute(object_)
            assert status == Metric.OK  # nosec B101  # used for unit tests
            return metric.result

        # Possible severity values
        MANDATORY = 0
        REQUIRED = 1
        ADVISORY = 2

        # Possible returned values by the following functions
        OK = 0
        FAILED = 1
        ERROR = 2
        # new 2023 R1, stands for NA
        NO_RULE = 3


from .sck import SCK


class Rule(_Rule):
    """Base class for all rules."""

    # set NA to OK until it is implemented
    # new 2023 R1: NA is there but named NO_RULE: let's keep NA
    try:
        NA = _Rule.NO_RULE
    except BaseException:
        NA = 0

    def __init__(
        self,
        id: str,
        label: str,
        category: str,
        severity: int,
        types: Optional[List[type]] = None,
        kinds: Optional[List[SCK]] = None,
        **kwargs,
    ):
        # discrimination of SCADE objects when the class isn't enough
        # compute the list of types when kinds is specified
        if kinds:
            types = [kind.value[0] for kind in kinds]
            self.kinds = kinds
        else:
            self.kinds = None
        # store the types, useful for unit tests
        self.types = types
        super().__init__(id, label, category, severity, types, **kwargs)
        self.violations = {}

    def on_stop(self) -> int:
        """Flush the violations."""
        # 2024 R2: crash when calling add_rule_status from on_stop
        # for (object_, local_id), (status, message) in self.violations.items():
        #     try:
        #         # 2024 R2 and above
        #         super().add_rule_status(object_, status, message, local_id)
        #     except TypeError:
        #         super().add_rule_status(object_, status, message)
        self.violations = {}
        return Rule.OK

    def add_rule_status(
        self,
        object_: suite.Object,
        status: int,
        message: str,
        local_id: str = '',
    ) -> None:
        """Register the violation."""
        key = (object_, local_id)
        # 2024 R2: crash when calling add_rule_status from on_stop
        # --> call add_rule_status right now if not already present
        # self.violations[key] = (status, message)
        if key not in self.violations:
            self.violations[key] = (status, message)
            try:
                # 2024 R2 and above
                super().add_rule_status(object_, status, message, local_id)
            except TypeError:
                super().add_rule_status(object_, status, message)

    def get_closest_annotatable(self, object_: suite.Object) -> suite.Object:
        """Return the closest container that can be annotated; Can be the object itself."""
        if isinstance(object_, suite.Edge):
            object_ = object_.src_equation
        if isinstance(object_, suite.PresentationElement):
            object_ = object_.presentable
        while not isinstance(object_, suite.Annotable):
            object_ = object_.owner
        # exceptions
        if isinstance(object_, suite.NamedType):
            if object_.is_generic():
                # generic types do not have an oid: return the operator
                return object_.owner
        elif isinstance(object_, suite.Type):
            # only named types can be annotated: recurse
            return self.get_closest_annotatable(object_.owner)
        return object_

    def on_check(self, object_: suite.Object, parameter: str = '') -> int:
        """Apply the rule to the input if it is compatible with the registered kinds."""
        if self.accept_kind(object_):
            return self.on_check_ex(object_, parameter)
        else:
            return Rule.NA

    def on_check_ex(self, object_: suite.Object, parameter: str = '') -> int:
        """Apply the rule to the input object."""
        # must not be called if on_check is redefined
        return Rule.ERROR

    def accept_kind(self, object_: suite.Object):
        """Return whether the input is compatible with the registered kinds."""
        if not self.kinds:
            return True

        for kind in self.kinds:
            type, filter = kind.value
            if isinstance(object_, type) and filter(object_):
                return True
        return False

    def parse_values(self, parameter: str):
        """Compile a string containing comma separated values into a dictionary."""
        d = {}
        for values in parameter.split(','):
            try:
                name, value = values.split('=')
                d[name.strip()] = value.strip()
            except BaseException:
                return None
        return d
