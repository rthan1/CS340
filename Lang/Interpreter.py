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

from typing import Dict, List, Tuple, Optional

from Tokenizer import Tokenizer
from Encoder import Encoder


class Interpreter:
    """
    Interpreter that wires Tokenizer and Encoder and exposes
    high-level processing methods for CLI/IDE.
    """

    def __init__(self, verbose: bool = False) -> None:
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
        self.verbose: bool = verbose
        self.variables: Dict[str, int] = {}

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
        self.variables.clear()

    def set_verbose(self, verbose: bool) -> None:
        self.verbose = verbose

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
        # Tokenize (Tokenizer already removes trailing comments with '#')
        tokens = Tokenizer.tokenize_line(line)

        # Verbose: show tokens as typed (without virtual terminator)
        display_lines: List[str] = []
        if self.verbose and tokens:
            display_lines.append("Tokens: " + " ".join(tokens))

        # Encode tokens for IDs and tables
        encoded = self.encoder.encode_tokens(tokens)

        # Track new table entries in verbose mode
        for item in encoded:
            kind = str(item['kind'])
            lex = str(item['lexeme'])
            code = int(item['code'])
            is_new = bool(item['is_new'])
            if not self.verbose:
                continue
            if kind == 'Symbol' and is_new:
                display_lines.append(f"Adding {lex} to symbol table with id {code}")
            if kind == 'Literal' and is_new:
                display_lines.append(f"Adding {lex} to literal table with id {code}")

        # Build TokenIDs, appending virtual ';' (203) if needed
        line_codes: List[int] = [int(item['code']) for item in encoded]
        has_semicolon = bool(tokens) and tokens[-1] == ';'
        if not has_semicolon and tokens:
            # Append virtual semicolon code to line IDs and program stream
            VIRTUAL_SEMI_CODE = 203
            line_codes.append(VIRTUAL_SEMI_CODE)
            # Also record in program code stream to mirror execution
            self.encoder.program_codes.append(VIRTUAL_SEMI_CODE)

        if self.verbose and line_codes:
            display_lines.append("TokenIDs: " + " ".join(str(c) for c in line_codes))

        # Drive CONO table and execute semantics
        code_generators_called: List[str] = []
        try:
            code_generators_called = self._execute_cono_and_run(tokens, has_semicolon)
        except Exception as exec_err:
            raise exec_err

        if self.verbose and code_generators_called:
            display_lines.append("Code generators called: " + " ".join(code_generators_called))

        return self._interactive_line_no, display_lines, line_codes

    def _execute_cono_and_run(self, tokens: List[str], has_semicolon: bool) -> List[str]:
        if not tokens:
            return []

        # Build op sequence (keywords and operators only)
        OPS = {"integer", "input", "print", "=", "(", ")", ";"}
        op_seq: List[str] = [t for t in tokens if t in OPS]
        if not has_semicolon and op_seq and op_seq[-1] != ';':
            op_seq.append(';')

        # CONO mapping
        CONO: Dict[Tuple[str, str], str] = {
            ("integer", "="): "start_define",
            ("integer", ";"): "end_define",
            ("input", "("): "start_input",
            ("print", "("): "start_print",
            ("(", ")"): "end_paren",
            (")", ";"): "no_op",
        }

        generators_called: List[str] = []
        for i in range(len(op_seq) - 1):
            pair = (op_seq[i], op_seq[i + 1])
            gen = CONO.get(pair)
            if gen is None:
                raise Exception(f"Syntax error: invalid token pair {pair}")
            generators_called.append(gen)

        # Execute semantics based on the first keyword
        first_op: Optional[str] = next((t for t in op_seq if t in {"integer", "input", "print"}), None)
        if first_op == "integer":
            self._exec_declaration(tokens)
        elif first_op == "input":
            self._exec_input(tokens)
        elif first_op == "print":
            self._exec_print(tokens)
        else:
            # Empty or comment-only line
            pass

        return generators_called

    def _expect_identifier_after(self, tokens: List[str], keyword_index: int) -> str:
        if keyword_index + 1 >= len(tokens):
            raise Exception("Syntax error: expected identifier")
        ident = tokens[keyword_index + 1]
        if ident in {"integer", "input", "print", "=", "(", ")", ";"}:
            raise Exception("Syntax error: expected identifier")
        return ident

    def _exec_declaration(self, tokens: List[str]) -> None:
        # Pattern: integer IDENT ; | integer IDENT = INT ;
        try:
            k = tokens.index("integer")
        except ValueError:
            raise Exception("Syntax error in declaration")
        ident = self._expect_identifier_after(tokens, k)

        value: int = 0
        if '=' in tokens:
            eq_index = tokens.index('=')
            if eq_index + 1 >= len(tokens):
                raise Exception("Syntax error: expected initializer after '='")
            lit = tokens[eq_index + 1]
            if not lit.isdigit():
                raise Exception("Syntax error: initializer must be integer literal")
            value = int(lit)
        self.variables[ident] = value

    def _exec_input(self, tokens: List[str]) -> None:
        # Pattern: input ( IDENT ) ;
        try:
            lpar = tokens.index('(')
            rpar = tokens.index(')')
        except ValueError:
            raise Exception("Syntax error: input requires parentheses")
        if rpar - lpar != 2:
            raise Exception("Syntax error: input takes exactly one identifier")
        ident = tokens[lpar + 1]
        if ident in {"integer", "input", "print", "=", "(", ")", ";"}:
            raise Exception("Syntax error: expected identifier in input")
        if ident not in self.variables:
            raise Exception(f"Runtime error: variable '{ident}' is not declared")
        try:
            user_val_str = input("=> ")
            user_val = int(user_val_str.strip())
        except Exception:
            raise Exception("Runtime error: input must be an integer")
        self.variables[ident] = user_val

    def _exec_print(self, tokens: List[str]) -> None:
        # Pattern: print ( IDENT | INT ) ;
        try:
            lpar = tokens.index('(')
            rpar = tokens.index(')')
        except ValueError:
            raise Exception("Syntax error: print requires parentheses")
        if rpar - lpar != 2:
            raise Exception("Syntax error: print takes exactly one operand")
        operand = tokens[lpar + 1]
        if operand.isdigit():
            value = int(operand)
        else:
            if operand not in self.variables:
                raise Exception(f"Runtime error: variable '{operand}' is not declared")
            value = self.variables[operand]
        print(value)

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

