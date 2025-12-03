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

    """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize components and session state     *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def __init__(self, verbose: bool = False) -> None:
        self.tokenizer = Tokenizer()
        self.encoder = Encoder()
        self._interactive_line_no = 0
        self.verbose: bool = verbose
        self.variables: Dict[str, int] = {}
        # Track multi-line blocks for indentation-based parsing
        self.in_block: bool = False
        self.block_lines: List[Tuple[str, int]] = []  # (line_text, indent_level)
        self.base_indent: int = 0

    """
        /**********************************************************
        * METHOD: reset_session                                   *
        * DESCRIPTION: Reset encoder/tables, counters, and blocks *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def reset_session(self) -> None:
        self.encoder.reset()
        self._interactive_line_no = 0
        self.variables.clear()
        self.in_block = False
        self.block_lines.clear()
        self.base_indent = 0

    """
        /**********************************************************
        * METHOD: set_verbose                                     *
        * DESCRIPTION: Enable or disable verbose tracing          *
        * PARAMETERS: verbose (bool)                              *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def set_verbose(self, verbose: bool) -> None:
        self.verbose = verbose

    """
        /**********************************************************
        * METHOD: process_line                                    *
        * DESCRIPTION: Tokenize and encode a single line;         *
        *              maintains session tables and codes         *
        * PARAMETERS: line (str)                                  *
        * RETURN VALUE: (line_no, display_lines, line_codes,      *
        *                print_outputs)                           *
        **********************************************************/
    """
    def process_line(self, line: str) -> Tuple[int, List[str], List[int], List[int]]:
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

    """
        /**********************************************************
        * METHOD: _get_indent_level                               *
        * DESCRIPTION: Compute indentation level of a source line *
        * PARAMETERS: line (str)                                  *
        * RETURN VALUE: indent (int)                              *
        **********************************************************/
    """
    def _get_indent_level(self, line: str) -> int:
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += 4
            else:
                break
        return indent

    """
        /**********************************************************
        * METHOD: _eval_condition                                 *
        * DESCRIPTION: Evaluate a comparison expression for if/   *
        *              elif/while conditions                      *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: bool                                      *
        **********************************************************/
    """
    def _eval_condition(self, tokens: List[str]) -> bool:
        # Find the comparison operator
        comp_ops = ['==', '!=', '<=', '>=', '<', '>']
        op_index = -1
        op = None
        
        for i, tok in enumerate(tokens):
            if tok in comp_ops:
                op_index = i
                op = tok
                break
        
        if op_index == -1:
            raise Exception("Syntax error: condition must contain comparison operator")
        
        # Split into left and right expressions
        left_tokens = tokens[:op_index]
        right_tokens = tokens[op_index + 1:]
        
        if not left_tokens or not right_tokens:
            raise Exception("Syntax error: invalid condition")
        
        # Evaluate both sides
        left_val = self._eval_pythonic_expr(left_tokens)
        right_val = self._eval_pythonic_expr(right_tokens)
        
        # Apply comparison
        if op == '==':
            return left_val == right_val
        elif op == '!=':
            return left_val != right_val
        elif op == '<':
            return left_val < right_val
        elif op == '>':
            return left_val > right_val
        elif op == '<=':
            return left_val <= right_val
        elif op == '>=':
            return left_val >= right_val
        else:
            raise Exception(f"Unknown comparison operator: {op}")

    """
        /**********************************************************
        * METHOD: _execute_block                                  *
        * DESCRIPTION: Execute a block of indented statements     *
        * PARAMETERS: lines (List[str])                           *
        * RETURN VALUE: (code_generators, print_outputs)          *
        **********************************************************/
    """
    def _execute_block(self, lines: List[str]) -> Tuple[List[str], List[int]]:
        generators: List[str] = []
        outputs: List[int] = []

        idx = 0
        while idx < len(lines):
            line = lines[idx]
            stripped = line.strip()
            if not stripped:
                idx += 1
                continue

            tokens = Tokenizer.tokenize_line(stripped)
            if not tokens:
                idx += 1
                continue

            # Always encode tokens so symbol/literal tables and program codes stay in sync
            self.encoder.encode_tokens(tokens)

            first_tok = tokens[0]

            if first_tok == 'if':
                header_indent = self._get_indent_level(line)
                condition_tokens = self._extract_condition_tokens(tokens)
                block_lines, next_idx = self._parse_indented_block_from_lines(
                    lines, idx + 1, header_indent
                )
                if_gens, if_outs, after_idx = self._execute_if_statement(
                    condition_tokens, block_lines, lines, next_idx
                )
                generators.extend(if_gens)
                outputs.extend(if_outs)
                idx = after_idx
            elif first_tok == 'while':
                header_indent = self._get_indent_level(line)
                condition_tokens = self._extract_condition_tokens(tokens)
                block_lines, next_idx = self._parse_indented_block_from_lines(
                    lines, idx + 1, header_indent
                )
                while_gens, while_outs = self._execute_while_loop(
                    condition_tokens, block_lines
                )
                generators.extend(while_gens)
                outputs.extend(while_outs)
                idx = next_idx
            else:
                has_semi = tokens[-1] == ';'
                if not has_semi:
                    tokens.append(';')
                line_gens, line_outs = self._execute_cono_and_run(tokens, has_semi)
                generators.extend(line_gens)
                outputs.extend(line_outs)
                idx += 1

        return generators, outputs

    """
        /**********************************************************
        * METHOD: _parse_indented_block_from_lines                *
        * DESCRIPTION: Collect lines belonging to an indented     *
        *              block following a control statement        *
        * PARAMETERS: lines (List[str]), start_idx (int),         *
        *              base_indent (int)                          *
        * RETURN VALUE: (block_lines, end_index)                  *
        **********************************************************/
    """
    def _parse_indented_block_from_lines(self, lines: List[str], start_idx: int, base_indent: int) -> Tuple[List[str], int]:
        block: List[str] = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                i += 1
                continue
            
            indent = self._get_indent_level(line)
            
            # If indent is back to base level or less, block is done
            if indent <= base_indent:
                break
            
            block.append(line)
            i += 1
        
        return block, i

    """
        /**********************************************************
        * METHOD: _execute_if_statement                           *
        * DESCRIPTION: Execute an if/elif/else chain using        *
        *              indentation-based blocks                   *
        * PARAMETERS: condition_tokens (List[str]),               *
        *              block_lines (List[str]),                   *
        *              all_lines (List[str]), start_idx (int)     *
        * RETURN VALUE: (code_generators, print_outputs,          *
        *               next_line_index)                          *
        **********************************************************/
    """
    def _execute_if_statement(self, condition_tokens: List[str], block_lines: List[str],
                              all_lines: List[str], start_idx: int) -> Tuple[List[str], List[int], int]:
        generators: List[str] = ["NOP", "SIF"]
        outputs: List[int] = []
        
        # Determine comparison operator for code generator
        comp_ops_map = {
            '==': 'CEQ', '!=': 'CNE',
            '<': 'CLT', '>': 'CGT',
            '<=': 'CLE', '>=': 'CGE'
        }
        comp_gen = "CMP"
        for tok in condition_tokens:
            if tok in comp_ops_map:
                comp_gen = comp_ops_map[tok]
                break
        
        generators.extend(["Ld", comp_gen])
        
        # Evaluate condition
        condition_result = self._eval_condition(condition_tokens)
        
        if condition_result:
            # Execute if block
            block_gens, block_outs = self._execute_block(block_lines)
            generators.extend(block_gens)
            outputs.extend(block_outs)
            
            # Skip any elif/else blocks
            next_idx = start_idx
            base_indent = self._get_indent_level(all_lines[start_idx - len(block_lines) - 1]) if start_idx > len(block_lines) else 0
            
            while next_idx < len(all_lines):
                line = all_lines[next_idx]
                stripped = line.strip()
                
                if not stripped:
                    next_idx += 1
                    continue
                
                indent = self._get_indent_level(line)
                if indent > base_indent:
                    next_idx += 1
                    continue
                
                tokens = Tokenizer.tokenize_line(stripped)
                if tokens and tokens[0] in ['elif', 'else']:
                    # Skip this branch
                    _, next_idx = self._parse_indented_block_from_lines(all_lines, next_idx + 1, indent)
                else:
                    break
            
            generators.append("EIF")
            return generators, outputs, next_idx
        else:
            # Check for elif/else
            next_idx = start_idx
            base_indent = self._get_indent_level(all_lines[start_idx - len(block_lines) - 1]) if start_idx > len(block_lines) else 0
            
            while next_idx < len(all_lines):
                line = all_lines[next_idx]
                stripped = line.strip()
                
                if not stripped:
                    next_idx += 1
                    continue
                
                indent = self._get_indent_level(line)
                if indent != base_indent:
                    next_idx += 1
                    continue
                
                tokens = Tokenizer.tokenize_line(stripped)
                if not tokens:
                    next_idx += 1
                    continue
                
                if tokens[0] == 'elif':
                    generators.append("ELS")
                    # Parse elif condition
                    elif_cond_tokens = self._extract_condition_tokens(tokens)
                    elif_block, next_idx = self._parse_indented_block_from_lines(all_lines, next_idx + 1, indent)
                    
                    # Recursively handle elif as a new if
                    elif_gens, elif_outs, next_idx = self._execute_if_statement(
                        elif_cond_tokens, elif_block, all_lines, next_idx
                    )
                    generators.extend(elif_gens)
                    outputs.extend(elif_outs)
                    return generators, outputs, next_idx
                    
                elif tokens[0] == 'else':
                    generators.append("ELS")
                    # Parse else block
                    else_block, next_idx = self._parse_indented_block_from_lines(all_lines, next_idx + 1, indent)
                    
                    # Execute else block
                    block_gens, block_outs = self._execute_block(else_block)
                    generators.extend(block_gens)
                    outputs.extend(block_outs)
                    generators.append("EIF")
                    return generators, outputs, next_idx
                else:
                    break
            
            generators.append("EIF")
            return generators, outputs, next_idx

    """
        /**********************************************************
        * METHOD: _execute_while_loop                             *
        * DESCRIPTION: Execute a while loop with indentation-     *
        *              based body                                 *
        * PARAMETERS: condition_tokens (List[str]),                *
        *              block_lines (List[str])                    *
        * RETURN VALUE: (code_generators, print_outputs)          *
        **********************************************************/
    """
    def _execute_while_loop(self, condition_tokens: List[str], block_lines: List[str]) -> Tuple[List[str], List[int]]:
        generators: List[str] = ["NOP", "Swh"]
        outputs: List[int] = []
        
        # Determine comparison operator for code generator
        comp_ops_map = {
            '==': 'CEQ', '!=': 'CNE',
            '<': 'CLT', '>': 'CGT',
            '<=': 'CLE', '>=': 'CGE'
        }
        comp_gen = "CMP"
        for tok in condition_tokens:
            if tok in comp_ops_map:
                comp_gen = comp_ops_map[tok]
                break
        
        generators.extend(["Ld", comp_gen])
        
        # Execute loop
        max_iterations = 10000  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            # Check condition
            try:
                condition_result = self._eval_condition(condition_tokens)
            except Exception:
                break
            
            if not condition_result:
                break
            
            # Execute block
            block_gens, block_outs = self._execute_block(block_lines)
            outputs.extend(block_outs)
            
            iteration += 1
        
        if iteration >= max_iterations:
            raise Exception("Runtime error: loop exceeded maximum iterations")
        
        generators.append("Ewh")
        return generators, outputs

    """
        /**********************************************************
        * METHOD: _extract_condition_tokens                       *
        * DESCRIPTION: Extract the condition expression from an   *
        *              if/elif/while statement                    *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: List[str] (condition tokens)              *
        **********************************************************/
    """
    def _extract_condition_tokens(self, tokens: List[str]) -> List[str]:
        if '(' not in tokens or ')' not in tokens:
            raise Exception("Syntax error: condition must be in parentheses")
        
        lpar_idx = tokens.index('(')
        rpar_idx = tokens.index(')')
        
        if rpar_idx <= lpar_idx + 1:
            raise Exception("Syntax error: empty condition")
        
        return tokens[lpar_idx + 1:rpar_idx]

    """
        /**********************************************************
        * METHOD: _handle_control_flow_statement                  *
        * DESCRIPTION: Handle an inner if/while encountered       *
        *              during block execution                     *
        * PARAMETERS: line (str), all_lines (List[str])           *
        * RETURN VALUE: (code_generators, print_outputs)          *
        **********************************************************/
    """
    def _handle_control_flow_statement(self, line: str, all_lines: List[str]) -> Tuple[List[str], List[int]]:
        tokens = Tokenizer.tokenize_line(line.strip())
        if not tokens:
            return [], []
        first_tok = tokens[0]
        if first_tok not in ["if", "while"]:
            has_semi = tokens[-1] == ';'
            if not has_semi:
                tokens.append(';')
            return self._execute_cono_and_run(tokens, has_semi)

        header_indent = self._get_indent_level(line)
        condition_tokens = self._extract_condition_tokens(tokens)
        block_lines, next_idx = self._parse_indented_block_from_lines(
            all_lines, all_lines.index(line) + 1, header_indent
        )

        if first_tok == "if":
            gens, outs, _ = self._execute_if_statement(
                condition_tokens, block_lines, all_lines, next_idx
            )
            return gens, outs

        gens, outs = self._execute_while_loop(condition_tokens, block_lines)
        return gens, outs

    """
        /**********************************************************
        * METHOD: _execute_cono_and_run                           *
        * DESCRIPTION: Drive CONO-style dispatch for single-line  *
        *              declarations, I/O, assignments, and exprs  *
        * PARAMETERS: tokens (List[str]), has_semicolon (bool)    *
        * RETURN VALUE: (code_generators, print_outputs)          *
        **********************************************************/
    """
    def _execute_cono_and_run(self, tokens: List[str], has_semicolon: bool) -> Tuple[List[str], List[int]]:
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

    """
        /**********************************************************
        * METHOD: _eval_pythonic_expr                             *
        * DESCRIPTION: Evaluate an arithmetic expression using    *
        *              Python semantics with integer-only result  *
        * PARAMETERS: expr_tokens (List[str])                     *
        * RETURN VALUE: int                                       *
        **********************************************************/
    """
    def _eval_pythonic_expr(self, expr_tokens: List[str]) -> int:
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

    """
        /**********************************************************
        * METHOD: _exec_assignment                                *
        * DESCRIPTION: Execute an assignment of the form          *
        *              IDENT = expression ;                       *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def _exec_assignment(self, tokens: List[str]) -> None:
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

    """
        /**********************************************************
        * METHOD: _exec_expression                                *
        * DESCRIPTION: Evaluate a bare expression statement and   *
        *              discard its value                          *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def _exec_expression(self, tokens: List[str]) -> None:
        if not tokens:
            return

        core = tokens[:-1] if tokens[-1] == ';' else list(tokens)
        if not core:
            return

        _ = self._eval_pythonic_expr(core)

    """
        /**********************************************************
        * METHOD: _expect_identifier_after                        *
        * DESCRIPTION: Return identifier token following a        *
        *              keyword, enforcing syntax rules            *
        * PARAMETERS: tokens (List[str]), keyword_index (int)     *
        * RETURN VALUE: ident (str)                               *
        **********************************************************/
    """
    def _expect_identifier_after(self, tokens: List[str], keyword_index: int) -> str:
        if keyword_index + 1 >= len(tokens):
            raise Exception("Syntax error: expected identifier")
        ident = tokens[keyword_index + 1]
        if ident in {"integer", "input", "print", "=", "(", ")", ";"}:
            raise Exception("Syntax error: expected identifier")
        return ident

    """
        /**********************************************************
        * METHOD: _exec_declaration                               *
        * DESCRIPTION: Execute an integer variable declaration     *
        *              with optional initializer                  *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
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

    """
        /**********************************************************
        * METHOD: _exec_input                                     *
        * DESCRIPTION: Execute an input statement and store user   *
        *              integer into a declared variable           *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
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

    """
        /**********************************************************
        * METHOD: _exec_print                                     *
        * DESCRIPTION: Execute a print statement and return value  *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: value printed (int)                       *
        **********************************************************/
    """
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

    """
        /**********************************************************
        * METHOD: process_source_with_blocks                      *
        * DESCRIPTION: Execute multi-line source with if/elif/    *
        *              else and while blocks using indentation    *
        * PARAMETERS: source_text (str)                           *
        * RETURN VALUE: (display_lines, print_outputs)            *
        **********************************************************/
    """
    def process_source_with_blocks(self, source_text: str) -> Tuple[List[str], List[int]]:
        lines = source_text.split('\n')
        all_display_lines: List[str] = []
        all_outputs: List[int] = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            tokens = Tokenizer.tokenize_line(stripped)
            if not tokens:
                i += 1
                continue
            
            first_tok = tokens[0]
            
            if first_tok == 'if':
                # Parse if statement with indented block
                base_indent = self._get_indent_level(line)
                condition_tokens = self._extract_condition_tokens(tokens)
                block_lines, next_idx = self._parse_indented_block_from_lines(lines, i + 1, base_indent)
                
                # Execute if statement
                generators, outputs, next_idx = self._execute_if_statement(
                    condition_tokens, block_lines, lines, i + len(block_lines) + 1
                )
                
                if self.verbose:
                    all_display_lines.append(f"{i+1}. {stripped}")
                    all_display_lines.append("Code generators called: " + " ".join(generators))
                    all_display_lines.append("")
                
                all_outputs.extend(outputs)
                i = next_idx
                
            elif first_tok == 'while':
                # Parse while loop with indented block
                base_indent = self._get_indent_level(line)
                condition_tokens = self._extract_condition_tokens(tokens)
                block_lines, next_idx = self._parse_indented_block_from_lines(lines, i + 1, base_indent)
                
                # Execute while loop
                generators, outputs = self._execute_while_loop(condition_tokens, block_lines)
                
                if self.verbose:
                    all_display_lines.append(f"{i+1}. {stripped}")
                    all_display_lines.append("Code generators called: " + " ".join(generators))
                    all_display_lines.append("")
                
                all_outputs.extend(outputs)
                i = next_idx
                
            else:
                # Regular statement (not control flow)
                self._interactive_line_no += 1
                line_no, display_lines, _, print_outputs = self.process_line(stripped)
                all_display_lines.extend(display_lines)
                all_outputs.extend(print_outputs)
                i += 1
        
        return all_display_lines, all_outputs

    """
        /**********************************************************
        * METHOD: compile_source                                  *
        * DESCRIPTION: Compile in-memory text, returning per-line *
        *              encodings, tables, and program codes       *
        * PARAMETERS: source_text (str)                           *
        * RETURN VALUE: dict                                      *
        **********************************************************/
    """
    def compile_source(self, source_text: str) -> Dict[str, object]:
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

    """
        /**********************************************************
        * METHOD: compile_file                                    *
        * DESCRIPTION: Compile a file path using compile_source   *
        * PARAMETERS: file_path (str)                             *
        * RETURN VALUE: dict                                      *
        **********************************************************/
    """
    def compile_file(self, file_path: str) -> Dict[str, object]:
        with open(file_path, 'r') as f:
            text = f.read()
        return self.compile_source(text)

