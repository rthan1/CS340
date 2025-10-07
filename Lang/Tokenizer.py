"""
/*******************************************************************
*                   Tokenizer for the Lang Language                *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 9/4/25                                                  *
*    REQUIREMENT: Assignment number 3                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Provides tokenization utilities for the Lang programming      *
*    language, including line and file tokenization and formatted  *
*    token output.                                                 *
*                                                                  *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Andrew Olvera and Dean Zeller. *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
"""

import re


class Tokenizer:
    """
    Tokenizer class that breaks down Lang source code into tokens
    """
    
    # Define keywords for the Lang language
    KEYWORDS = {
        'if', 'else', 'elif', 'while', 'for', 'def', 'return', 
        'print', 'input', 'output', 'class', 'import', 'from',
        'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None',
        'break', 'continue', 'pass', 'try', 'except', 'finally'
    }
    
    # Define operators and symbols
    OPERATORS = {
        '+', '-', '*', '/', '//', '%', '**',
        '=', '==', '!=', '<', '>', '<=', '>=',
        '+=', '-=', '*=', '/=',
        '&', '|', '^', '~', '<<', '>>',
        'and', 'or', 'not'
    }
    
    DELIMITERS = {
        '(', ')', '[', ']', '{', '}',
        ',', ':', ';', '.', '@', '->', '=>'
    }
    
    def __init__(self):
        """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize a Tokenizer instance            *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        pass
    
    @staticmethod
    def tokenize_line(line):
        """
        /**********************************************************
        * METHOD: tokenize_line                                   *
        * DESCRIPTION: Tokenize a single line of Lang code        *
        * PARAMETERS: line (str) - input code line                *
        * RETURN VALUE: list[str] - tokens for the line           *
        **********************************************************/
        """
        tokens = []
        line = line.strip()
        
        # Handle empty lines
        if not line:
            return tokens
        
        # Regular expression pattern to match tokens
        # This pattern matches:
        # 1. Multi-character operators (>=, <=, ==, !=, //, **, +=, -=, *=, /=, <<, >>)
        # 2. Numbers (integers and floats)
        # 3. Identifiers and keywords
        # 4. String literals (single or double quoted)
        # 5. Single character operators and delimiters
        pattern = r'''
            (>=|<=|==|!=|//|\*\*|\+=|-=|\*=|/=|<<|>>|->|=>)  # Multi-char operators
            |(\d+\.\d+|\d+)                                    # Numbers (float or int)
            |([a-zA-Z_]\w*)                                    # Identifiers/keywords
            |("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')            # String literals
            |([\+\-\*/%<>=\(\)\[\]\{\},;:\.@&\|\^\~!])        # Single-char operators/delimiters
        '''
        
        matches = re.finditer(pattern, line, re.VERBOSE)
        
        for match in matches:
            token = match.group(0)
            tokens.append(token)
        
        return tokens
    
    @staticmethod
    def format_tokens(tokens):
        """
        /**********************************************************
        * METHOD: format_tokens                                   *
        * DESCRIPTION: Format tokens separated by vertical bars   *
        * PARAMETERS: tokens (list[str]) - tokens to format       *
        * RETURN VALUE: str - tokens joined with " | "            *
        **********************************************************/
        """
        if not tokens:
            return ""
        return " | ".join(tokens)
    
    @staticmethod
    def tokenize_file(file_path):
        """
        /**********************************************************
        * METHOD: tokenize_file                                   *
        * DESCRIPTION: Tokenize an entire file                    *
        * PARAMETERS: file_path (str) - path to source file       *
        * RETURN VALUE: list[tuple] - (line_no, content, tokens)  *
        **********************************************************/
        """
        result = []
        
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                line_content = line.rstrip('\n')
                tokens = Tokenizer.tokenize_line(line_content)
                result.append((line_num, line_content, tokens))
            
            return result
            
        except Exception as e:
            raise Exception(f"Error tokenizing file: {e}")
    
    @staticmethod
    def print_tokenized_file(file_path):
        """
        /**********************************************************
        * METHOD: print_tokenized_file                            *
        * DESCRIPTION: Print tokenized lines with eol/eof         *
        * PARAMETERS: file_path (str) - path to source file       *
        * RETURN VALUE: None                                      *
        **********************************************************/
        """
        try:
            tokenized_lines = Tokenizer.tokenize_file(file_path)
            
            for line_num, line_content, tokens in tokenized_lines:
                # Print the line with line number
                print(f"Line {line_num:3d}: {line_content}")
                
                # Print tokens if the line has any
                if tokens:
                    tokens_with_eol = tokens + ['eol']
                    formatted_tokens = Tokenizer.format_tokens(tokens_with_eol)
                    print(f"         {formatted_tokens}")
                else:
                    # Empty line still gets eol
                    print(f"         eol")
            
            # Print EOF token at the end
            print("         eof")
            
        except Exception as e:
            raise Exception(f"Error printing tokenized file: {e}")


def main():
    """
    /**********************************************************
    * METHOD: main                                            *
    * DESCRIPTION: Entry point for testing the tokenizer      *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        Tokenizer.print_tokenized_file(file_path)
    else:
        print("Usage: python Tokenizer.py <file_path>")


if __name__ == "__main__":
    main()
