__author__ = "cloudstrife9999"

from re import match
from typing import Optional

if hasattr(__import__("re"), "Match"):
    from re import Match
else:
    from re.sre_compile import compile
    
    Match = type(compile('', 0).match(''))

from common import global_config
from strings import *


class PrologOutputParser():
    def __init__(self):
        self.__result_regex: str = global_config[result_regex_key]

    def is_output_empty(self, output: str) -> bool:
        return output == ""

    def has_error_message(self, output: str) -> bool:
        for error_pattern in global_config[error_patterns_key]:
            if error_pattern in output:
                return True
        
        return False

    def parse_output(self, output: str) -> str:
        m: Optional[Match[str]] = match(self.__result_regex, output)

        if m:
            return str(m[0])
        else:
            return output

    def check_output(self, result: str, expected_result: str, out_of_order_allowed: bool=True) -> bool:
        if not result or not result.strip():
            return False

        outcome: bool = result == expected_result
        
        # If order does not matter.
        if not outcome and out_of_order_allowed:
            outcome |= self.__ordered_match(result, expected_result)

        return outcome

    def __ordered_match(self, unordered: str, ordered: str) -> bool:
        assert match(self.__result_regex, ordered)

        if not match(self.__result_regex, unordered):
            return False

        # Same number of characters.
        if len(unordered) != len(ordered):
            return False

        unordered = unordered.replace("].", "").replace("Res = [", "")
        ordered = ordered.replace("].", "").replace("Res = [", "")

        u_tokens: list = self.__tokenise(raw=unordered)
        o_tokens: list = self.__tokenise(raw=ordered)

        # Same number of tokens.
        if len(u_tokens) != len(o_tokens):
            return False

        u_tokens.sort()
        o_tokens.sort()

        return u_tokens == o_tokens

    def __tokenise(self, raw: str) -> list:
        '''
        Assumes `output` is of the form [...], [...], [...], [...], ...
        '''
        tokens: list = []

        i: int = 0

        for index in range(len(raw)):
            if raw[index] == "[":
                i = index
            elif raw[index] == "]":
                tokens.append(raw[i:(index + 1)])

        return tokens