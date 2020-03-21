from re import match, sre_compile

try:
    from re import Match
except:
    Match = type(sre_compile.compile('', 0).match(''))


class PrologOutputParser():
    def __init__(self):
        self.__result_regex: str = "Res = \[.*\]\."

    def is_output_empty(self, output: str) -> bool:
        return output == ""

    def has_error_message(self, output: str, error_pattern="ERROR:") -> bool:
        return match(error_pattern, output)

    def parse_output(self, output: str) -> str:
        m: Match = match(self.__result_regex, output)

        if m:
            return m[0]
        else:
            return ""

    def check_output(self, result: str, expected_result: str, out_of_order_allowed: bool=True) -> bool:
        if not result:
            return False

        outcome: bool = result == expected_result
        
        # If order does not matter.
        if not  outcome and out_of_order_allowed:
            outcome |= self.__ordered_match(result, expected_result)

        return outcome

    def __ordered_match(self, unordered: str, ordered: str) -> bool:
        assert match(self.__result_regex, unordered) and match(self.__result_regex, ordered)

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