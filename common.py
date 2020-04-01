from strings import *

global_config: dict = {
    required_software_key: [
        "swipl"
    ],
    notable_extensions_key: [".pl"],
    common_misspellings_key: {
        "breath_first.pl": "breadth_first.pl",
        "efficient_search.pl": "efficient_searches.pl"
    },
    parts_weights_key: {},
    timeout_key: None,
    code_directory_key: "",
    tests_directory_key: "",
    keep_receiving_if_received_key: [
        "Welcome to",
        "Warning",
        "true.",
        "help(",
        "?-"
    ],
    error_patterns_key: [
        "ERROR:",
        "global-stack",
        "Searching:"
    ],
    result_regex_key: None,
    exceptions_debug_key: False
}

storage: dict = {
    test_cases_with_errors_key: []
}