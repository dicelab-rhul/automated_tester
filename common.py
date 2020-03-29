config: dict = {
    "required_software": [
        "swipl"
    ],
    "parts_weights": {},
    "timeout": None,
    "code_directory": "",
    "test_directory": "",
    "keep_receiving_if_received": [
        "Welcome to",
        "Warning",
        "true.",
        "help(",
        "?-"
    ],
    "error_patterns": [
        "ERROR:",
        "global-stack",
        "Searching:"
    ],
    "exceptions_debug": False
}

storage: dict = {
    "test_cases_with_errors": []
}