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
    print("  - Type 'verbose on|off' to toggle verbose trace")
    print("  - Type 'reset' to clear tables/state")
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
    line_no, display_lines, _, print_outputs = interpreter.process_line(line)
    print(f"{line_no}. {line}")
    for msg in display_lines:
        print(msg)

    # In verbose mode, show a [console] section so users can see the actual
    # program output separate from the trace. In non-verbose mode, just print
    # the outputs like a normal interpreter.
    if interpreter.verbose and print_outputs:
        print("[console]")
        for val in print_outputs:
            print(val)
    elif not interpreter.verbose:
        for val in print_outputs:
            print(val)

    print()


def compile_file(filename, verbose: bool = False):
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
    
    print(f"\n[EXECUTING] {filename}")
    print("-" * 60)
    try:
        interpreter = Interpreter(verbose=verbose)
        interpreter.reset_session()

        with open(filename, 'r') as f:
            source = f.read()
        
        # Use the new process_source_with_blocks method for control flow support
        try:
            display_lines, all_outputs = interpreter.process_source_with_blocks(source)
            
            if verbose:
                for msg in display_lines:
                    print(msg)
            
            print("-" * 60)
            print(f"[EXECUTION COMPLETE]")

            if verbose and all_outputs:
                print("[console]")
                for val in all_outputs:
                    print(val)
            elif not verbose:
                for val in all_outputs:
                    print(val)
        except Exception as e:
            print(f"Error: {e}")

        print()
    except Exception as e:
        print(f"Error: {e}")


def interactive_mode(verbose_default: bool = False):
    """
    /**********************************************************
    * METHOD: interactive_mode                                *
    * DESCRIPTION: Run the interactive REPL for Lang          *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    print_banner()
    interpreter = Interpreter(verbose=verbose_default)
    verbose = bool(verbose_default)
    
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
                compile_file(filename, verbose=verbose)
            elif user_input.lower() == 'reset':
                interpreter.reset_session()
                print("Session reset. Tables cleared.\n")
            elif user_input.lower().startswith('verbose '):
                _, _, val = user_input.partition(' ')
                val = val.strip().lower()
                if val in ['on', 'off']:
                    verbose = (val == 'on')
                    interpreter.set_verbose(verbose)
                    print(f"Verbose {'enabled' if verbose else 'disabled'}.\n")
                else:
                    print("Usage: verbose on|off\n")
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


def main(verbose_default: bool = False):
    """
    /**********************************************************
    * METHOD: main                                            *
    * DESCRIPTION: Entry point for the Lang CLI               *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
    """
    # Flags: --verbose enables verbose by default in REPL
    args = sys.argv[1:]
    if args and args[0] == '--verbose':
        verbose_default = True
        args = args[1:]

    if args:
        # File mode - execute the specified file
        filename = args[0]
        compile_file(filename, verbose=verbose_default)
    else:
        # Interactive mode
        interactive_mode(verbose_default=verbose_default)


if __name__ == "__main__":
    main()
