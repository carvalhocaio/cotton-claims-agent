from datetime import date

from chains.claim_extraction import ClaimExtract


def test_convert_string_to_date_with_valid_format():
    assert ClaimExtract._convert_string_to_date("2026-06-03") == date(2026, 6, 3)

def test_convert_string_to_date_with_invalid_format_returns_none():
    assert ClaimExtract._convert_string_to_date("June 3rd, 2026") is None


def test_convert_string_to_date_with_none_returns_none():
    assert ClaimExtract._convert_string_to_date(None) is None

def test_computed_fields_derive_from_raw_date_strings():
    claim = ClaimExtract(claim_date_str="2026-06-03", response_deadline_str="2026-06-10")

    assert claim.claim_date == date(2026, 6, 3)
    assert claim.response_deadline == date(2026, 6, 10)

def test_raw_date_strings_are_excluded_from_model_dump():
    claim = ClaimExtract(claim_date_str="2026-06-03")
    dumped = claim.model_dump()

    assert "claim_date_str" not in dumped
    assert dumped["claim_date"] == date(2026, 6, 3)
