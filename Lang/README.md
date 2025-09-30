# Lang Programming Language - Assignment 3 Setup

## Overview
This is the setup for Assignment 3, which provides an interactive interpreter for the Lang programming language.

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
- Type `compile <filename>` to compile a file
- Type `exit` or `quit` to exit the interpreter

### 2. File Compilation Mode
Compile a text file by reading all lines and displaying them with line numbers.

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
Line   2: x = 10
Line   3: y = 20
Line   4: z = x + y
Line   5: print(z)
Line   6: result = z * 2
Line   7: output(result)
------------------------------------------------------------
[COMPILATION COMPLETE] Processed 7 line(s)
```

## Files Structure
- `cli.py` - Main command-line interface and entry point
- `ide_entry.py` - IDE entry point (calls cli.py main function)
- `Tokenizer.py` - (To be implemented in next phase)
- `Parser.py` - (To be implemented in next phase)
- `Interpreter.py` - (To be implemented in next phase)
- `test-txt/` - Directory containing test files

## Next Steps (Assignment 3)
The next phase will implement the Tokenizer to break down input lines into tokens for further processing.
