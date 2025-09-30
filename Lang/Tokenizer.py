"""
Tokenizer for the Lang Programming Language
Assignment 3: Tokenization Implementation
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
        """Initialize the tokenizer"""
        pass
    
    @staticmethod
    def tokenize_line(line):
        """
        Tokenize a single line of code
        
        Args:
            line: A string representing a line of code
            
        Returns:
            A list of tokens
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
        Format tokens for display, separated by vertical bars
        
        Args:
            tokens: List of token strings
            
        Returns:
            A formatted string with tokens separated by |
        """
        if not tokens:
            return ""
        return " | ".join(tokens)
    
    @staticmethod
    def tokenize_file(file_path):
        """
        Tokenize an entire file
        
        Args:
            file_path: Path to the file to tokenize
            
        Returns:
            A list of tuples (line_number, line_content, tokens)
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
        Print a tokenized file with line numbers and tokens
        
        Args:
            file_path: Path to the file to tokenize and print
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
    Main function for testing the tokenizer
    """
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        Tokenizer.print_tokenized_file(file_path)
    else:
        print("Usage: python Tokenizer.py <file_path>")


if __name__ == "__main__":
    main()
