# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

from czudf_toolkit import annotate


def test_annotate():
    @annotate("string,int->string")
    class Repeat:
        def evaluate(self, x: str, y: int) -> str:
            return x * y if x and y > 0 else ""

    repeat = Repeat()
    assert repeat.evaluate("x", 3) == "xxx"
