from requests import Response, HTTPError

_MAX_BODY_LENGTH = 1024
_ERROR_MESSAGE = "{code} {type} Error for url: {method} {url}\nResponse: {text}"

class ServerHttpError(HTTPError):
    pass


class ClientHttpError(HTTPError):
    pass

class WrongHttpStatusError(HTTPError):
    pass


def strip_trailing_slash(url):
    """
    remove url's trailing slash

    :param url:
    :return:
    """
    if url.endswith("/"):
        url = url[:-1]
    return url


def assert_http_status(response: Response, expected: list = []) -> Response:
    error_type = None

    if expected and response.status_code not in expected:
        error_type = "Wrong Status Code"
        err_cls = WrongHttpStatusError
    elif 400 <= response.status_code < 500:
        error_type = "Client"
        err_cls = ClientHttpError
    elif 500 <= response.status_code < 600:
        error_type = "Server"
        err_cls = ServerHttpError

    if error_type:
        http_error_msg = _ERROR_MESSAGE.format(
            type=error_type,
            code=response.status_code,
            method=response.request.method,
            url=response.url,
            text=body_to_str(response),
        )
        raise err_cls(http_error_msg, response=response)

    return response


def body_to_str(response: Response) -> str:
    return response.text[:_MAX_BODY_LENGTH].strip()
