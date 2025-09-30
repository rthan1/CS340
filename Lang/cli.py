"""
Command-Line Interface for the Lang Programming Language
Assignment 3 Setup
"""

import sys
import os


def print_banner():
    """Print the welcome banner for the Lang interpreter"""
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
    Execute a single line of code
    Currently just echoes back the input (Assignment 3 setup)
    """
    print(f"[EXECUTING] {line}")
    print(f"Output: {line}")
    print()


def compile_file(filename):
    """
    Compile a file by reading all lines and displaying with line numbers
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
        
        print("-" * 60)
        print(f"[COMPILATION COMPLETE] Processed {len(lines)} line(s)")
        print()
        
    except Exception as e:
        print(f"Error reading file: {e}")


def interactive_mode():
    """
    Run the interactive REPL (Read-Eval-Print Loop)
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
    """Main entry point for the CLI"""
    if len(sys.argv) > 1:
        # File mode - compile the specified file
        filename = sys.argv[1]
        compile_file(filename)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
