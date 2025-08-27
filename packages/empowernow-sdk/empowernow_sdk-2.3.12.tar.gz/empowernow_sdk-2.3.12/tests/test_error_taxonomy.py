import pytest
from empowernow_common.oauth.security import validate_url_security
from empowernow_common.errors import UrlValidationError, ErrorCode


def test_url_validation_error_code():
    with pytest.raises(UrlValidationError) as exc:
        validate_url_security("http://localhost")
    assert exc.value.error_code == ErrorCode.URL_INVALID
