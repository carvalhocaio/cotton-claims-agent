from typing import cast

import pytest

from chains.claim_extraction import CLAIM_PARSER_CHAIN, ClaimExtract

pytestmark = pytest.mark.integration


def test_extracts_contamination_claim_with_hvi_and_exposure(claims):
    result = cast(ClaimExtract, CLAIM_PARSER_CHAIN.invoke({"message": claims[0]}))

    assert result.claiming_party is not None
    assert "Meridian" in result.claiming_party
    assert result.max_potential_exposure == 180_000.0
    assert result.hvi_findings is not None
    assert result.hvi_findings.micronaire == pytest.approx(3.2)


def test_extracts_weight_dispute_without_hvi_findings(claims):
    result = cast(ClaimExtract, CLAIM_PARSER_CHAIN.invoke({"message": claims[3]}))

    assert result.claiming_party is not None
    assert "Vale do Cerrado" in result.claiming_party
    assert result.hvi_findings is None
