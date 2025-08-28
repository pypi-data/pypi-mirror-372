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

"""Implements the NameStructureType rule."""

if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.resolve()))


import scade.model.suite as suite

from ansys.scade.design_rules.utils.rule import Rule


class EqSetHasEqs(Rule):
    """Implements the rule interface."""

    def __init__(
        self,
        id='id_0020',
        label='Equation set content',
        description=(
            'An equation set shall contain only:\n'
            '* Equations\n* If nodes\n* When branches\n* Assertions'
        ),
        category='Traceability',
        severity=Rule.ADVISORY,
        **kwargs,
    ):
        super().__init__(
            id=id,
            label=label,
            description=description,
            category=category,
            severity=severity,
            types=[suite.EquationSet],
            has_parameter=False,
            **kwargs,
        )

    def on_check(self, equation_set: suite.EquationSet, parameter: str = '') -> int:
        """Return the evaluation status for the input object."""
        paths = [
            presentable.get_full_path()
            for presentable in equation_set.presentables
            if not self.accept(presentable)
        ]
        if paths:
            status = Rule.FAILED
            message = 'equation set {} shall not contain \n\t{}'
            self.set_message(message.format(equation_set.name, '\n\t'.join(paths)))
        else:
            status = Rule.OK
        return status

    def accept(self, presentable: suite.Presentable) -> bool:
        """
        Return whether the element is eligible for belonging to an equation set.

        This method can be overridden in a derived class to consider different elements.
        """
        return (
            isinstance(presentable, suite.Equation)
            or isinstance(presentable, suite.Assertion)
            or isinstance(presentable, suite.IfNode)
            or isinstance(presentable, suite.WhenBranch)
        )


if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    EqSetHasEqs()
