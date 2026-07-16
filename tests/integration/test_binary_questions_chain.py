from typing import cast

import pytest

from chains.binary_questions import BINARY_QUESTION_CHAIN, BinaryAnswer

pytestmark = pytest.mark.integration


def test_no_confirmed_contamitation_in_weight_dispute(claims):
    result = cast(
        BinaryAnswer,
        BINARY_QUESTION_CHAIN.invoke(
            {
                "question": "Houve contaminação confirmada no lote?",
                "message": claims[3],
            }
        ),
    )
    assert result.answer is False
