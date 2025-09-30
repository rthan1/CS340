# Lang Programming Language - Assignment 3: Tokenization

## Overview
This is Assignment 3, which implements a tokenizer for the Lang programming language. The system can read source files, display them with line numbers, and tokenize each line into its component tokens.

## Features

### 1. Interactive Mode (REPL)
Run the interpreter in interactive mode where you can execute commands one line at a time.

**Usage:**
```bash
python cli.py
```
or
```bash
python ide_entry.py
```

**Commands:**
- Type any code to execute it (currently echoes back the input)
- Type `compile <filename>` to compile and tokenize a file
- Type `exit` or `quit` to exit the interpreter

### 2. File Compilation and Tokenization Mode
Compile a text file by reading all lines, displaying them with line numbers, and showing the tokenized output. Each line is followed by its tokens separated by vertical bars (|), with `eol` marking the end of each line and `eof` marking the end of the file.

**Usage:**
```bash
python cli.py <filename>
```

**Example:**
```bash
python cli.py test-txt/operation.txt
```

## Example Usage

### Interactive Mode Example:
```
Lang> x = 10
[EXECUTING] x = 10
Output: x = 10

Lang> y = 20
[EXECUTING] y = 20
Output: y = 20

Lang> compile test-txt/operation.txt
[COMPILING] test-txt/operation.txt
------------------------------------------------------------
Line   1: 1 + 5
         1 | + | 5 | eol
Line   2: x = 10
         x | = | 10 | eol
Line   3: y = 20
         y | = | 20 | eol
Line   4: z = x + y
         z | = | x | + | y | eol
Line   5: print(z)
         print | ( | z | ) | eol
Line   6: result = z * 2
         result | = | z | * | 2 | eol
Line   7: output(result)
         output | ( | result | ) | eol
         eof
------------------------------------------------------------
[COMPILATION COMPLETE] Processed 7 line(s)
```

## Files Structure
- `cli.py` - Main command-line interface and entry point with tokenization support
- `ide_entry.py` - IDE entry point (calls cli.py main function)
- `Tokenizer.py` - **✓ Implemented** - Tokenizes Lang source code into individual tokens
- `Parser.py` - (To be implemented in next phase)
- `Interpreter.py` - (To be implemented in next phase)
- `test-txt/` - Directory containing test files
- `test_tokenizer.py` - Test script to demonstrate tokenization

## Tokenization Features

The tokenizer recognizes and handles:
- **Keywords**: `if`, `else`, `elif`, `while`, `for`, `def`, `return`, `print`, `input`, `output`, etc.
- **Operators**: `+`, `-`, `*`, `/`, `//`, `%`, `**`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`, etc.
- **Delimiters**: `(`, `)`, `[`, `]`, `{`, `}`, `,`, `:`, `;`, `.`, `@`
- **Identifiers**: Variable and function names
- **Literals**: Numbers (integers and floats), strings (single or double quoted)
- **Special Tokens**: `eol` (end of line) and `eof` (end of file)

## GUI Interface

The project also includes a PyQt6-based GUI (`LangDesgnAssignment2/ChatGPTGUI.py`) that provides:
- Code editor with syntax highlighting support
- Output console showing compilation and tokenization results
- Graphics panel (for future use)
- Buttons to execute lines, compile all code, load files, and clear output

## Next Steps
The next phase will implement the Parser to build an Abstract Syntax Tree (AST) from the tokens.
