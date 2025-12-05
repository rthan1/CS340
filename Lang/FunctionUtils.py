"""
/*******************************************************************
*                 Function Utilities for Lang Language             *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 12/5/25                                                 *
*    REQUIREMENT: Assignment extension                             *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Provides function definition storage, environment stack       *
*    management, and function call handling for the Lang           *
*    interpreter to support user-defined functions with            *
*    parameters and optional return values.                        *
*                                                                  *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
"""

from typing import Dict, List, Tuple, Optional, Any


class ReturnValue(Exception):
    """
    Exception used to signal an early return from a function.
    Carries the return value and any accumulated print outputs with it.
    """
    def __init__(self, value: int, outputs: list = None):
        self.value = value
        self.outputs = outputs if outputs is not None else []
        super().__init__()


class FunctionUtils:
    """
    Manages function definitions, environment stack, and function calls
    for the Lang interpreter.
    """

    """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize function table and env stack    *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def __init__(self):
        # Store function definitions: name -> (param_names, body_lines)
        self.functions: Dict[str, Tuple[List[str], List[str]]] = {}
        
        # Environment stack: list of variable dicts
        # The last element is the current environment
        self.env_stack: List[Dict[str, int]] = [{}]
    
    """
        /**********************************************************
        * METHOD: reset                                           *
        * DESCRIPTION: Clear all functions and reset env stack    *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def reset(self) -> None:
        self.functions.clear()
        self.env_stack = [{}]
    
    """
        /**********************************************************
        * METHOD: get_current_env                                 *
        * DESCRIPTION: Get the current environment (top of stack) *
        * PARAMETERS: None                                        *
        * RETURN VALUE: Dict[str, int]                            *
        **********************************************************/
    """
    def get_current_env(self) -> Dict[str, int]:
        return self.env_stack[-1]
    
    """
        /**********************************************************
        * METHOD: push_env                                        *
        * DESCRIPTION: Push a new environment onto the stack      *
        * PARAMETERS: new_env (Dict[str, int])                    *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def push_env(self, new_env: Dict[str, int]) -> None:
        self.env_stack.append(new_env)
    
    """
        /**********************************************************
        * METHOD: pop_env                                         *
        * DESCRIPTION: Pop the current environment from stack     *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def pop_env(self) -> None:
        if len(self.env_stack) > 1:
            self.env_stack.pop()
    
    """
        /**********************************************************
        * METHOD: define_function                                 *
        * DESCRIPTION: Store a function definition                *
        * PARAMETERS: name (str), param_names (List[str]),        *
        *             body_lines (List[str])                      *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def define_function(self, name: str, param_names: List[str], body_lines: List[str]) -> None:
        self.functions[name] = (param_names, body_lines)
    
    """
        /**********************************************************
        * METHOD: has_function                                    *
        * DESCRIPTION: Check if a function is defined             *
        * PARAMETERS: name (str)                                  *
        * RETURN VALUE: bool                                      *
        **********************************************************/
    """
    def has_function(self, name: str) -> bool:
        return name in self.functions
    
    """
        /**********************************************************
        * METHOD: get_function                                    *
        * DESCRIPTION: Retrieve function definition               *
        * PARAMETERS: name (str)                                  *
        * RETURN VALUE: (param_names, body_lines)                 *
        **********************************************************/
    """
    def get_function(self, name: str) -> Tuple[List[str], List[str]]:
        if name not in self.functions:
            raise Exception(f"Runtime error: function '{name}' is not defined")
        return self.functions[name]
    
    """
        /**********************************************************
        * METHOD: parse_function_header                           *
        * DESCRIPTION: Parse func name(param1, param2): into      *
        *              name and parameter list                    *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: (func_name, param_names)                  *
        **********************************************************/
    """
    @staticmethod
    def parse_function_header(tokens: List[str]) -> Tuple[str, List[str]]:
        # Expected: func name ( param1 , param2 , ... ) :
        if len(tokens) < 4:
            raise Exception("Syntax error: invalid function definition")
        
        if tokens[0] != 'func':
            raise Exception("Syntax error: function definition must start with 'func'")
        
        func_name = tokens[1]
        
        if func_name in {'func', 'return', 'if', 'else', 'elif', 'while', 
                        'integer', 'input', 'print', '=', '(', ')', ';', ':'}:
            raise Exception(f"Syntax error: '{func_name}' cannot be used as function name")
        
        if '(' not in tokens or ')' not in tokens or ':' not in tokens:
            raise Exception("Syntax error: function definition must have '()', ':' ")
        
        lpar_idx = tokens.index('(')
        rpar_idx = tokens.index(')')
        colon_idx = tokens.index(':')
        
        if lpar_idx != 2:
            raise Exception("Syntax error: '(' must follow function name")
        
        if colon_idx != len(tokens) - 1:
            raise Exception("Syntax error: ':' must be at end of function header")
        
        # Extract parameters between parentheses
        param_tokens = tokens[lpar_idx + 1:rpar_idx]
        
        # Parse comma-separated parameters
        param_names: List[str] = []
        if param_tokens:
            # Split by comma
            current_param = []
            for tok in param_tokens:
                if tok == ',':
                    if current_param:
                        if len(current_param) != 1:
                            raise Exception("Syntax error: invalid parameter list")
                        param_names.append(current_param[0])
                        current_param = []
                else:
                    current_param.append(tok)
            
            # Add last parameter
            if current_param:
                if len(current_param) != 1:
                    raise Exception("Syntax error: invalid parameter list")
                param_names.append(current_param[0])
        
        # Validate parameter names
        for param in param_names:
            if param in {'func', 'return', 'if', 'else', 'elif', 'while',
                        'integer', 'input', 'print', '=', '(', ')', ';', ':'}:
                raise Exception(f"Syntax error: '{param}' cannot be used as parameter name")
        
        return func_name, param_names
    
    """
        /**********************************************************
        * METHOD: parse_function_call                             *
        * DESCRIPTION: Parse name(arg1, arg2) into name and args  *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: (func_name, arg_token_groups)             *
        **********************************************************/
    """
    @staticmethod
    def parse_function_call(tokens: List[str]) -> Tuple[str, List[List[str]]]:
        # Expected: name ( arg1 , arg2 , ... )
        if len(tokens) < 3:
            raise Exception("Syntax error: invalid function call")
        
        func_name = tokens[0]
        
        if '(' not in tokens or ')' not in tokens:
            raise Exception("Syntax error: function call must have parentheses")
        
        lpar_idx = tokens.index('(')
        rpar_idx = tokens.index(')')
        
        if lpar_idx != 1:
            raise Exception("Syntax error: '(' must follow function name in call")
        
        # Extract argument tokens between parentheses
        arg_tokens = tokens[lpar_idx + 1:rpar_idx]
        
        # Split arguments by comma
        arg_groups: List[List[str]] = []
        if arg_tokens:
            current_arg: List[str] = []
            for tok in arg_tokens:
                if tok == ',':
                    if current_arg:
                        arg_groups.append(current_arg)
                        current_arg = []
                else:
                    current_arg.append(tok)
            
            # Add last argument
            if current_arg:
                arg_groups.append(current_arg)
        
        return func_name, arg_groups
    
    """
        /**********************************************************
        * METHOD: looks_like_function_call                        *
        * DESCRIPTION: Check if tokens look like a function call  *
        * PARAMETERS: tokens (List[str])                          *
        * RETURN VALUE: bool                                      *
        **********************************************************/
    """
    @staticmethod
    def looks_like_function_call(tokens: List[str]) -> bool:
        # Pattern: identifier ( ... )
        if len(tokens) < 3:
            return False
        
        if tokens[0] in {'func', 'return', 'if', 'else', 'elif', 'while',
                        'integer', 'input', 'print'}:
            return False
        
        return tokens[1] == '(' and ')' in tokens

