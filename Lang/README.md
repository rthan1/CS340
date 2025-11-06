# Lang Programming Language - Assignment 4: Token Encoding

## Overview
This is Assignment 4, which adds integer-based token encoding on top of tokenization. The system assigns codes to keywords, operators, symbols, and literals, maintains symbol/literal tables, and prints program codes.

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
- Type any code to process it (encodes tokens and updates tables)
- Type `compile <filename>` to compile a file
- Type `reset` to clear symbol/literal tables for the session
- Type `exit` or `quit` to exit the interpreter

### 2. File Compilation and Encoding Mode
Compile a text file by reading all lines, displaying them with line numbers, and showing the encoded token lines. After all lines, the Symbol Table, Literal Table, and Program Codes are printed.

**Usage:**
```bash
python cli.py <filename>
```

**Example:**
```bash
python cli.py test-txt/encoding_sample.txt
```

## Example Usage

### Encoding Example (from assignment):
Input file `test-txt/encoding_sample.txt`:

```
SUM = 0;
for I goes from 1 to 10
SUM = SUM + I;
print(I);
```

Produces output like:

```
1. SUM = 0;
Symbol: SUM id 300 new symbol
Operation: = id 220
Literal: 0 id 700 new literal
Operation: ; id 201
2. for I goes from 1 to 10
Keyword: for id 105
Symbol: I id 301 new symbol
Keyword: goes id 107
Keyword: from id 108
Literal: 1 id 701 new literal
Keyword: to id 113
Literal: 10 id 702 new literal
3. SUM = SUM + I;
Symbol: SUM id 300
Operation: = id 220
Symbol: SUM id 300
Operation: + id 248
Symbol: I id 301
Operation: ; id 201
4. print(I);
Keyword: print id 153
Operation: ( id 235
Symbol: I id 301
Operation: ) id 236
Operation: ; id 201
Symbol Table
300 SUM
301 I
Literal Table
700 0
701 1
702 10
Program Codes
300 220 700 201 105 301 107 108 701 113
702 300 220 300 248 301 201 153 235 301
236 201
```

## Files Structure
- `cli.py` - CLI/REPL using `Interpreter` (encoding-aware)
- `ide_entry.py` - IDE entry point (calls cli.py main function)
- `Tokenizer.py` - Tokenizes Lang source code into tokens
- `Encoder.py` - **✓ Implemented** - Encodes tokens to integer codes and manages tables
- `Interpreter.py` - **✓ Implemented** - Orchestrates Tokenizer + Encoder
- `Parser.py` - (Placeholder for future assignment)
- `test-txt/` - Directory containing test files (includes `encoding_sample.txt`)

## Encoding Scheme

- Ranges:
  - Keywords: 100–199
  - Operators/Delimiters: 200–299
  - Symbols: 300–699
  - Literals (integers): 700–999
- Persistent tables per session:
  - Symbol table: first-come, first-served from 300
  - Literal table: first-come, first-served from 700
- Explicit codes (to match sample): `for=105`, `goes=107`, `from=108`, `to=113`, `print=153`, `;=201`, `=220`, `(=235`, `)=236`, `+=248`.

## GUI Interface

The project includes a PyQt6-based GUI (`LangDesgnAssignment2/ChatGPTGUI.py`) that uses `Interpreter` to produce encoding output and tables. It provides:
- Code editor
- Output console showing per-line encodings, Symbol/Literal tables, and Program Codes
- Graphics panel (for future use)
- Buttons to execute a single line, compile all code, load files, and clear output

## Next Steps
Implement the Parser to build an Abstract Syntax Tree (AST) from the tokens.
