def print_request_id(message, response):
    if "x-request-id" in response.headers:
        return message + " Request ID: " + response.headers["x-request-id"]
    else:
        return message