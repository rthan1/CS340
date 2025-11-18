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

    def process_line(self, line: str) -> Tuple[int, List[str], List[int], List[int]]:
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
        print_outputs: List[int] = []
        try:
            code_generators_called, print_outputs = self._execute_cono_and_run(tokens, has_semicolon)
        except Exception as exec_err:
            raise exec_err

        if self.verbose and code_generators_called:
            display_lines.append("Code generators called: " + " ".join(code_generators_called))

        # In verbose mode we no longer inline console outputs here; callers can
        # present a separate [console] section after all verbose traces.

        return self._interactive_line_no, display_lines, line_codes, print_outputs

    def _execute_cono_and_run(self, tokens: List[str], has_semicolon: bool) -> Tuple[List[str], List[int]]:
        """
        Drive a simplified CONO-style pass that both:
          - builds a list of code generators for verbose output
          - dispatches to the appropriate semantic executor

        For this assignment we support:
          - Declarations: integer x; / integer x = 10;
          - Input:        input(x);
          - Print:        print(x); or print(10);
          - Assignments:  x = expression;
          - Expressions:  expression;
        """
        if not tokens:
            return [], []

        # Ensure we have a terminating ';' token for semantic analysis
        work_tokens = list(tokens)
        if not has_semicolon and work_tokens and work_tokens[-1] != ';':
            work_tokens.append(';')

        generators_called: List[str] = []
        print_outputs: List[int] = []

        first_tok: Optional[str] = work_tokens[0] if work_tokens else None

        if first_tok == "integer":
            # Declaration: emit start/end define based on presence of '='
            if '=' in work_tokens:
                generators_called.extend(["start_define", "end_define"])
            else:
                generators_called.append("end_define")
            self._exec_declaration(work_tokens)

        elif first_tok == "input":
            # Pattern: input ( IDENT ) ;
            # Match the example: no_op start_input end_paren no_op
            generators_called.extend(["no_op", "start_input", "end_paren", "no_op"])
            self._exec_input(work_tokens)

        elif first_tok == "print":
            # Pattern: print ( IDENT | INT ) ;
            generators_called.extend(["start_print", "end_paren", "no_op"])
            val = self._exec_print(work_tokens)
            print_outputs.append(val)

        else:
            # Non-keyword statement: either an assignment "x = expr;"
            # or a bare expression "expr;" whose value is discarded.
            if '=' in work_tokens:
                generators_called.append("assign")
                self._exec_assignment(work_tokens)
            else:
                generators_called.append("evaluate")
                self._exec_expression(work_tokens)

        return generators_called, print_outputs

    def _eval_pythonic_expr(self, expr_tokens: List[str]) -> int:
        """
        Evaluate an arithmetic expression using Python semantics, with small
        adaptations to keep integers:
          - '/' is treated as integer division by mapping to '//'
          - '^' is treated as exponent by mapping to '**'
        """
        if not expr_tokens:
            raise Exception("Syntax error: empty expression")

        # Map Lang operators to Python operators
        python_tokens: List[str] = []
        for tok in expr_tokens:
            if tok == '/':
                python_tokens.append('//')
            elif tok == '^':
                python_tokens.append('**')
            else:
                python_tokens.append(tok)

        expr_str = " ".join(python_tokens)

        # Use only current variables as the evaluation environment
        env = dict(self.variables)

        try:
            value = eval(expr_str, {"__builtins__": None}, env)
        except ZeroDivisionError:
            raise Exception("Runtime error: division by zero")
        except NameError as e:
            raise Exception(f"Runtime error: {e}")
        except SyntaxError:
            raise Exception("Syntax error: invalid expression")
        except Exception as e:
            raise Exception(f"Runtime error: invalid expression: {e}")

        if not isinstance(value, int):
            raise Exception("Runtime error: expression must evaluate to an integer")

        return value

    def _exec_assignment(self, tokens: List[str]) -> None:
        """
        Execute an assignment statement of the form:
          IDENT = expression ;
        """
        if not tokens:
            return

        # Remove trailing ';' for analysis
        core = tokens[:-1] if tokens[-1] == ';' else list(tokens)
        if not core:
            return

        if '=' not in core:
            raise Exception("Syntax error: assignment requires '='")

        eq_index = core.index('=')
        lhs_tokens = core[:eq_index]
        rhs_tokens = core[eq_index + 1 :]

        if len(lhs_tokens) != 1:
            raise Exception("Syntax error: invalid assignment target")

        name = lhs_tokens[0]

        if name in {"integer", "input", "print", "=", "(", ")", ";"}:
            raise Exception("Syntax error: invalid assignment target")

        if name not in self.variables:
            raise Exception(f"Runtime error: variable '{name}' is not declared")

        if not rhs_tokens:
            raise Exception("Syntax error: expected expression after '='")

        value = self._eval_pythonic_expr(rhs_tokens)
        self.variables[name] = value

    def _exec_expression(self, tokens: List[str]) -> None:
        """
        Execute a bare expression statement of the form:
          expression ;
        The value is evaluated for errors and then discarded.
        """
        if not tokens:
            return

        core = tokens[:-1] if tokens[-1] == ';' else list(tokens)
        if not core:
            return

        _ = self._eval_pythonic_expr(core)

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
        return value

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

