"""
/*******************************************************************
*        CLI for the Lang Programming Language (Assignment 3)       *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 9/4/25                                                  *
*    REQUIREMENT: Assignment number 3                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Command-Line Interface (CLI) for interacting with the Lang    *
*    programming language. Provides an interactive REPL and file   *
*    compilation that displays line numbers and tokenized output.   *
*                                                                  *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
"""

import sys
import os
from Tokenizer import Tokenizer


def print_banner():
    """
    /**********************************************************
    * METHOD: print_banner                                    *
    * DESCRIPTION: Print the welcome banner for the Lang CLI  *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    print("=" * 60)
    print("  Lang Programming Language - Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  - Type any code to execute it")
    print("  - Type 'compile <filename>' to compile a file")
    print("  - Type 'exit' or 'quit' to exit")
    print("=" * 60)
    print()


def execute_line(line):
    """
    /**********************************************************
    * METHOD: execute_line                                    *
    * DESCRIPTION: Execute a single line of Lang code         *
    * PARAMETERS: line (str) - the code line to execute       *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    print(f"[EXECUTING] {line}")
    print(f"Output: {line}")
    print()


def compile_file(filename):
    """
    /**********************************************************
    * METHOD: compile_file                                    *
    * DESCRIPTION: Compile a file and display tokenized lines *
    * PARAMETERS: filename (str) - path to the file           *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
    
    print(f"\n[COMPILING] {filename}")
    print("-" * 60)
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        for line_num, line in enumerate(lines, start=1):
            # Remove trailing newline for display
            line_content = line.rstrip('\n')
            print(f"Line {line_num:3d}: {line_content}")
            
            # Tokenize the line
            tokens = Tokenizer.tokenize_line(line_content)
            
            # Add eol token
            if tokens:
                tokens_with_eol = tokens + ['eol']
            else:
                tokens_with_eol = ['eol']
            
            # Format and print tokens
            formatted_tokens = Tokenizer.format_tokens(tokens_with_eol)
            print(f"         {formatted_tokens}")
        
        # Print eof token at the end
        print("         eof")
        
        print("-" * 60)
        print(f"[COMPILATION COMPLETE] Processed {len(lines)} line(s)")
        print()
        
    except Exception as e:
        print(f"Error reading file: {e}")


def interactive_mode():
    """
    /**********************************************************
    * METHOD: interactive_mode                                *
    * DESCRIPTION: Run the interactive REPL for Lang          *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    print_banner()
    
    while True:
        try:
            # Get user input
            user_input = input("Lang> ").strip()
            
            # Skip empty lines
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting Lang interpreter. Goodbye!")
                break
            
            # Check for compile command
            if user_input.lower().startswith('compile '):
                filename = user_input[8:].strip()
                compile_file(filename)
            else:
                # Execute the line
                execute_line(user_input)
                
        except KeyboardInterrupt:
            print("\n\nKeyboardInterrupt detected. Exiting...")
            break
        except EOFError:
            print("\n\nEOF detected. Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


def main():
    """
    /**********************************************************
    * METHOD: main                                            *
    * DESCRIPTION: Entry point for the Lang CLI               *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    if len(sys.argv) > 1:
        # File mode - compile the specified file
        filename = sys.argv[1]
        compile_file(filename)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
