def validate_response(response: dict) -> bool:
    """
    Validates api response.
    Simple pass-through for now, or checks for 'code' == 0/200.
    """
    if not response:
        return False
    # WEEX often uses 'code': '00000' or similar for success
    # Adjust based on actual API doc if needed.
    return True
