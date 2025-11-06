"""
/*******************************************************************
*                  Interpreter for the Lang Language               *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 11/6/25                                                 *
*    REQUIREMENT: Assignment number 4                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Orchestrates tokenization and encoding. Owns Tokenizer and    *
*    Encoder. Provides APIs for processing lines, files, and       *
*    in-memory source text, and exposes symbol/literal tables and  *
*    program codes per the assignment requirements.                *
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

from Tokenizer import Tokenizer
from Encoder import Encoder


class Interpreter:
    """
    Interpreter that wires Tokenizer and Encoder and exposes
    high-level processing methods for CLI/IDE.
    """

    def __init__(self) -> None:
        """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize components and session state     *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        self.tokenizer = Tokenizer()
        self.encoder = Encoder()
        self._interactive_line_no = 0

    def reset_session(self) -> None:
        """
        /**********************************************************
        * METHOD: reset_session                                   *
        * DESCRIPTION: Reset encoder/tables and line counter       *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        self.encoder.reset()
        self._interactive_line_no = 0

    def process_line(self, line: str) -> Tuple[int, List[str], List[int]]:
        """
        /**********************************************************
        * METHOD: process_line                                    *
        * DESCRIPTION: Tokenize and encode a single line;         *
        *              maintains session tables and codes         *
        * PARAMETERS: line (str)                                  *
        * RETURN VALUE: (line_no, display_lines, line_codes)      *
        **********************************************************/
        """
        self._interactive_line_no += 1
        tokens = Tokenizer.tokenize_line(line)
        encoded = self.encoder.encode_tokens(tokens)
        display_lines: List[str] = []
        line_codes: List[int] = []
        for item in encoded:
            kind = str(item['kind'])
            lex = str(item['lexeme'])
            code = int(item['code'])
            is_new = bool(item['is_new'])
            if kind == 'Keyword':
                display_lines.append(f"Keyword: {lex} id {code}")
            elif kind == 'Operation':
                display_lines.append(f"Operation: {lex} id {code}")
            elif kind == 'Symbol':
                suffix = " new symbol" if is_new else ""
                display_lines.append(f"Symbol: {lex} id {code}{suffix}")
            elif kind == 'Literal':
                suffix = " new literal" if is_new else ""
                display_lines.append(f"Literal: {lex} id {code}{suffix}")
            line_codes.append(code)
        return self._interactive_line_no, display_lines, line_codes

    def compile_source(self, source_text: str) -> Dict[str, object]:
        """
        /**********************************************************
        * METHOD: compile_source                                  *
        * DESCRIPTION: Compile in-memory text, returning per-line  *
        *              encodings, tables, and program codes        *
        * PARAMETERS: source_text (str)                            *
        * RETURN VALUE: dict                                       *
        **********************************************************/
        """
        self.encoder.reset()
        per_line: List[Tuple[int, str, List[str]]] = []
        lines = source_text.split('\n')
        for idx, original in enumerate(lines, start=1):
            tokens = Tokenizer.tokenize_line(original)
            encoded = self.encoder.encode_tokens(tokens)
            display_lines: List[str] = []
            for item in encoded:
                kind = str(item['kind'])
                lex = str(item['lexeme'])
                code = int(item['code'])
                is_new = bool(item['is_new'])
                if kind == 'Keyword':
                    display_lines.append(f"Keyword: {lex} id {code}")
                elif kind == 'Operation':
                    display_lines.append(f"Operation: {lex} id {code}")
                elif kind == 'Symbol':
                    suffix = " new symbol" if is_new else ""
                    display_lines.append(f"Symbol: {lex} id {code}{suffix}")
                elif kind == 'Literal':
                    suffix = " new literal" if is_new else ""
                    display_lines.append(f"Literal: {lex} id {code}{suffix}")
            per_line.append((idx, original, display_lines))

        # Build tables sorted by code
        symbol_table_dict = self.encoder.get_symbol_table()
        literal_table_dict = self.encoder.get_literal_table()
        symbols_sorted: List[Tuple[int, str]] = sorted(
            ((code, name) for name, code in symbol_table_dict.items()), key=lambda x: x[0]
        )
        literals_sorted: List[Tuple[int, int]] = sorted(
            ((code, value) for value, code in literal_table_dict.items()), key=lambda x: x[0]
        )
        program_codes: List[int] = self.encoder.get_program_codes()

        return {
            'per_line': per_line,  # list of (line_no, original, display_lines)
            'symbol_table': symbols_sorted,  # list of (code, name)
            'literal_table': literals_sorted,  # list of (code, value)
            'program_codes': program_codes,  # list[int]
        }

    def compile_file(self, file_path: str) -> Dict[str, object]:
        """
        /**********************************************************
        * METHOD: compile_file                                    *
        * DESCRIPTION: Compile a file path using compile_source     *
        * PARAMETERS: file_path (str)                               *
        * RETURN VALUE: dict                                        *
        **********************************************************/
        """
        with open(file_path, 'r') as f:
            text = f.read()
        return self.compile_source(text)

