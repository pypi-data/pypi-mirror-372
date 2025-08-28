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

"""Implements the LLROrNetOnly rule."""

if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.resolve()))


import scade.model.suite as suite

from ansys.scade.design_rules.traceability.llr_only import LLROnly

# ignore F401: Rule required for the documentation process
from ansys.scade.design_rules.utils.rule import Rule  # noqa: F401


class LLROrNetOnly(LLROnly):
    """Implements the rule interface."""

    def __init__(self, id='id_0098', **kwargs):
        super().__init__(id=id, **kwargs)

    def is_llr(self, traceable: suite.Traceable) -> bool:
        """Return whether the element is a contributing element for traceability."""
        return (
            isinstance(traceable, suite.NetDiagram) and not traceable.equation_sets
        ) or super().is_llr(traceable)


if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    LLROrNetOnly()
