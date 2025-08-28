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

"""Implements the AnnNotesPresentAndNotEmpty rule."""

if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.resolve()))


import scade.model.suite as suite

from ansys.scade.design_rules.utils.annotations import (
    AnnotationRule,
    ArgumentParser,
    get_first_note_by_type,
    is_ann_note_value_defined_and_get_value,
)
from ansys.scade.design_rules.utils.rule import Rule


class AnnNotesPresentAndNotEmpty(AnnotationRule):
    """Implements the rule interface."""

    def __init__(
        self,
        id='id_0108',
        category='annotations',
        severity=Rule.REQUIRED,
        parameter='-t AnnType_1 -n AT1_Field1 AT1_Field2 AT1_Field3',
        types=None,
        kinds=None,
        description=(
            'Check if an element has a specific annotation note type attached to it. '
            'In addition it is checked that the given field elements are present and not empty.\n\n'
            'parameter:\n'
            "* '-t': Name of the annotation note type (e.g.: '-t AnnType')\n"
            "* '-n': Names of annotation note elements "
            '(e.g.: -n AT1_Field1 AT1_Field2 AT1_Field3)'
        ),
        label='AnnotationNotes present and not empty',
    ):
        if not types:
            types = [suite.Constant, suite.Operator]
        super().__init__(
            id=id,
            category=category,
            severity=severity,
            has_parameter=True,
            default_param=parameter,
            description=description,
            label=label,
            types=types,
            kinds=kinds,
        )

    def on_start(self, model: suite.Model, parameter: str = '') -> int:
        """Get the rule's parameters."""
        # minimal level of backward compatibility
        parameter = parameter.replace(',notes=', ' -n ').replace(';', ' ')
        status = super().on_start(model, parameter)
        if status == Rule.OK:
            assert self.options is not None  # nosec B101  # addresses linter
            self.names = self.options.names

        return status

    def add_arguments(self, parser: ArgumentParser):
        """Declare arguments in addition to the note type."""
        help = 'Names of the note elements'
        parser.add_argument(
            '-n', '--names', help=help, nargs='+', required=True, metavar='<attribute>'
        )

    def on_check_ex(self, object_: suite.Object, parameter: str = '') -> int:
        """Return the evaluation status for the input object."""
        # make sure object_ is annotatable since the selected types
        # can be customized
        if not isinstance(object_, suite.Annotable):
            return Rule.NA

        violation_text = self._check_annotation(object_)

        if violation_text:
            self.set_message(f'Annotation error for {object_.name}: {violation_text}')
            return Rule.FAILED
        return Rule.OK

    def _check_annotation(self, object_: suite.Annotable) -> str:
        """Check the annotation for the given object."""
        violations = []
        assert self.note_type is not None  # nosec B101  # addresses linter
        note = get_first_note_by_type(object_, self.note_type)
        if note is None:
            violations.append(f'Note missing: {self.note_type.name}')
        else:
            for name in self.names:
                defined, _ = is_ann_note_value_defined_and_get_value(note, name)
                if not defined:
                    violations.append(f'Name missing: {name}')

        return ', '.join(violations)


if __name__ == '__main__':  # pragma: no cover
    # rule instantiated outside of a package
    AnnNotesPresentAndNotEmpty()
