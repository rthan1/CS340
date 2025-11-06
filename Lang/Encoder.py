"""
/*******************************************************************
*                       Encoder for Lang Language                   *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 11/6/25                                                 *
*    REQUIREMENT: Assignment number 4                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Maps tokens to integer codes using assignment-specified ranges *
*    with persistent symbol and literal tables per session.         *
*                                                                  *
*    RANGES:                                                       *
*      100-199 Keywords                                            *
*      200-299 Operators/Delimiters                                *
*      300-699 Symbols (identifiers)                               *
*      700-999 Literals (integers)                                 *
*                                                                  *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
"""

from typing import Dict, List, Tuple


class Encoder:
    """
    Encoder that classifies tokens and assigns integer codes.
    Maintains symbol and literal tables and the program code stream.
    """

    # Explicit codes to match the provided example output
    KEYWORD_CODES: Dict[str, int] = {
        'if': 100,
        'while': 103,
        'for': 105,
        'return': 106,
        'goes': 107,
        'from': 108,
        'to': 113,
        'print': 153,
    }

    OPERATOR_CODES: Dict[str, int] = {
        ';': 201,
        '=': 220,
        '(': 235,
        ')': 236,
        '+': 248,
        # Additional operators can be added here as needed
    }

    SYMBOL_START_CODE: int = 300
    LITERAL_START_CODE: int = 700

    def __init__(self) -> None:
        """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize tables and counters              *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        self.reset()

    def reset(self) -> None:
        """
        /**********************************************************
        * METHOD: reset                                           *
        * DESCRIPTION: Clear symbol/literal tables and codes       *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        self.symbol_to_code: Dict[str, int] = {}
        self.literal_to_code: Dict[int, int] = {}
        self.next_symbol_code: int = self.SYMBOL_START_CODE
        self.next_literal_code: int = self.LITERAL_START_CODE
        self.program_codes: List[int] = []

    def encode_tokens(self, tokens: List[str]) -> List[Dict[str, object]]:
        """
        /**********************************************************
        * METHOD: encode_tokens                                   *
        * DESCRIPTION: Classify and encode tokens, updating       *
        *              tables and program code stream             *
        * PARAMETERS: tokens (list[str])                          *
        * RETURN VALUE: list[dict] with keys:                     *
        *   kind: 'Keyword'|'Operation'|'Symbol'|'Literal'        *
        *   lexeme: original token string                         *
        *   code: assigned integer code                           *
        *   is_new: bool (for Symbol/Literal only)                *
        **********************************************************/
        """
        encoded: List[Dict[str, object]] = []
        for tok in tokens:
            kind, code, is_new = self._encode_single(tok)
            self.program_codes.append(code)
            encoded.append({
                'kind': kind,
                'lexeme': tok,
                'code': code,
                'is_new': is_new,
            })
        return encoded

    def _encode_single(self, token: str) -> Tuple[str, int, bool]:
        # Keyword
        if token in self.KEYWORD_CODES:
            return 'Keyword', self.KEYWORD_CODES[token], False

        # Operator / delimiter
        if token in self.OPERATOR_CODES:
            return 'Operation', self.OPERATOR_CODES[token], False

        # Integer literal (only integer type per assignment)
        if token.isdigit():
            value = int(token)
            if value in self.literal_to_code:
                return 'Literal', self.literal_to_code[value], False
            code = self.next_literal_code
            self.literal_to_code[value] = code
            self.next_literal_code += 1
            return 'Literal', code, True

        # Symbol (identifier)
        if token in self.symbol_to_code:
            return 'Symbol', self.symbol_to_code[token], False
        code = self.next_symbol_code
        self.symbol_to_code[token] = code
        self.next_symbol_code += 1
        return 'Symbol', code, True

    def get_symbol_table(self) -> Dict[str, int]:
        return dict(self.symbol_to_code)

    def get_literal_table(self) -> Dict[int, int]:
        return dict(self.literal_to_code)

    def get_program_codes(self) -> List[int]:
        return list(self.program_codes)


