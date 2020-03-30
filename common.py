config: dict = {
    "required_software": [
        "swipl"
    ],
    "notable_extensions": [".pl"],
    "common_misspellings": {
        "breath_first.pl": "breadth_first.pl",
        "efficient_search.pl": "efficient_searches.pl"
    },
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