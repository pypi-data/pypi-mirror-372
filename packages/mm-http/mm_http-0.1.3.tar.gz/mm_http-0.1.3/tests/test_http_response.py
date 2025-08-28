from mm_result import Result

from mm_http import HttpError, HttpResponse


def test_to_result_ok_with_simple_value():
    """Test to_result_ok with a simple value."""
    response = HttpResponse(status_code=200, body='{"success": true}')
    result = response.to_result_ok(42)

    assert isinstance(result, Result)
    assert result.is_ok()
    assert result.value == 42
    assert result.extra and result.extra["status_code"] == 200


def test_to_result_ok_with_parsed_json():
    """Test to_result_ok with parsed JSON data."""
    response = HttpResponse(status_code=200, body='{"data": {"value": 123}}', headers={"content-type": "application/json"})
    parsed_value = response.parse_json_body("data.value")
    result = response.to_result_ok(parsed_value)

    assert result.is_ok()
    assert result.value == 123
    assert result.extra and result.extra["headers"]["content-type"] == "application/json"


def test_to_result_err_with_http_error():
    """Test to_result_err with HttpError."""
    response = HttpResponse(error=HttpError.TIMEOUT, error_message="Request timed out")
    result = response.to_result_err()

    assert result.is_err()
    assert result.error == HttpError.TIMEOUT
    assert result.extra and result.extra["error"] == "timeout"
    assert result.extra["error_message"] == "Request timed out"


def test_to_result_err_with_custom_error():
    """Test to_result_err with custom error message."""
    response = HttpResponse(status_code=404, error=HttpError.ERROR)
    result = response.to_result_err("Custom error message")

    assert result.is_err()
    assert result.error == "Custom error message"
    assert result.extra and result.extra["status_code"] == 404


def test_to_result_err_with_exception():
    """Test to_result_err with Exception object."""
    response = HttpResponse(error=HttpError.CONNECTION)
    custom_exception = ValueError("Connection failed")
    result = response.to_result_err(custom_exception)

    assert result.is_err()
    assert result.error == "ValueError: Connection failed"
    assert result.extra and result.extra["error"] == "connection"


def test_to_result_err_fallback():
    """Test to_result_err fallback to 'error' when no error is set."""
    response = HttpResponse(status_code=500)
    result = response.to_result_err()

    assert result.is_err()
    assert result.error == "error"
    assert result.extra and result.extra["status_code"] == 500


def test_result_methods_preserve_response_data():
    """Test that both methods preserve all response data in extra."""
    response = HttpResponse(
        status_code=201, error=None, error_message=None, body='{"created": "item"}', headers={"location": "/items/123"}
    )

    result = response.to_result_ok("success")

    expected_extra = {
        "status_code": 201,
        "error": None,
        "error_message": None,
        "body": '{"created": "item"}',
        "headers": {"location": "/items/123"},
    }

    assert result.extra == expected_extra


def test_integration_with_error_checking():
    """Test typical usage pattern with is_err() check."""
    # Success case
    response_ok = HttpResponse(status_code=200, body='{"value": 42}')

    if response_ok.is_err():
        result = response_ok.to_result_err()
    else:
        result = response_ok.to_result_ok(response_ok.parse_json_body("value"))

    assert result.is_ok()
    assert result.value == 42

    # Error case
    response_err = HttpResponse(error=HttpError.TIMEOUT)

    result = response_err.to_result_err() if response_err.is_err() else response_err.to_result_ok("should not happen")

    assert result.is_err()
    assert result.error == HttpError.TIMEOUT
