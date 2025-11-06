"""
/*********************************************************************************
*        CLI for the Lang Programming Language (Assignment 3)                    *
*                                                                                *
*    PROGRAMMER: Andrew Olvera                                                   *
*    COURSE: CS340 Program Language Design                                       *
*    DATE: 10/7/25                                                               *
*    REQUIREMENT: Assignment 3                                                   *
*                                                                                *
*    DESCRIPTION:                                                                *
*    Command-Line Interface (CLI) for interacting with the Lang                  *
*    programming language. Provides an interactive REPL and file                 *
*    compilation that displays line numbers and tokenized output.                *
*                                                                                *
*    COPYRIGHT:                                                                  *
*    This code is copyright (c)2025 Andrew Olvera, Ethan Nelson, and Dean Zeller.*
*                                                                                *
*    CREDITS:                                                                    *
*    ChatGPT                                                                     *
*                                                                                *
*********************************************************************************/
"""

import sys
import os
from Interpreter import Interpreter


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


def execute_line(interpreter: Interpreter, line: str):
    """
    /**********************************************************
    * METHOD: execute_line                                    *
    * DESCRIPTION: Execute a single line of Lang code         *
    * PARAMETERS: line (str) - the code line to execute       *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    line_no, display_lines, _ = interpreter.process_line(line)
    print(f"{line_no}. {line}")
    for msg in display_lines:
        print(msg)
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
        interpreter = Interpreter()
        result = interpreter.compile_file(filename)

        # Per-line output
        for line_no, original, display_lines in result['per_line']:
            print(f"{line_no}. {original}")
            for msg in display_lines:
                print(msg)

        # Tables
        print("Symbol Table")
        for code, name in result['symbol_table']:
            print(f"{code} {name}")
        print("Literal Table")
        for code, value in result['literal_table']:
            print(f"{code} {value}")
        # Program codes
        print("Program Codes")
        codes = result['program_codes']
        for i in range(0, len(codes), 10):
            chunk = codes[i:i+10]
            print(" ".join(str(c) for c in chunk))

        print("-" * 60)
        print(f"[COMPILATION COMPLETE] Processed {len(result['per_line'])} line(s)")
        print()
    except Exception as e:
        print(f"Error: {e}")


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
    interpreter = Interpreter()
    
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
            elif user_input.lower() == 'reset':
                interpreter.reset_session()
                print("Session reset. Tables cleared.\n")
            else:
                # Execute the line
                execute_line(interpreter, user_input)
                
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
