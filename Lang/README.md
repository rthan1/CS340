## Lang / EAR Technical Guide (Interpreter + GUI + 2D Graphics)

This document is a **technical reproduction guide** and a **narration-ready script** for a tutorial video. It explains how the project is built (modules, data flow, and runtime behavior) and how to reproduce it from the ground up.

> Note: The UI labels say “EAR”, but the runtime language implementation lives under `Lang/` and is driven through the PyQt6 GUI in `LangDesgnAssignment2/ChatGPTGUI.py`.

---

## What this project is

- **A small interpreted language** (statements + expressions + control flow + user-defined functions).
- **A token encoder** (assignment requirement): tokens are mapped to integer codes and stored in tables.
- **A PyQt6 IDE-style GUI** that executes code and shows output.
- **A 2D renderer** embedded in the GUI (`QGraphicsView`) that can draw shapes bound to Lang variables and animate them.

---

## Repo map (the parts you’ll show in the tutorial)

### Runtime / language implementation (`Lang/`)

- **`Tokenizer.py`**: converts source text into a token stream.
- **`Encoder.py`**: converts tokens into integer codes and maintains:
  - symbol table (identifiers)
  - literal table (integers)
  - program code stream (the encoded sequence)
- **`Interpreter.py`**: executes the language and orchestrates:
  - tokenization
  - encoding
  - evaluation/execution
  - function support (via `FunctionUtils`)
  - graphics calls (via `Renderer`)
- **`FunctionUtils.py`**: stores function definitions, manages environment stack, handles returns.
- **`Renderer.py`**: PyQt6 `QGraphicsView` renderer (shapes + animation loop).
- **`demo-ear/`**: example `.ear` scripts you can load in the GUI.

### GUI (`LangDesgnAssignment2/`)

- **`ChatGPTGUI.py`**: the main UI for running code and embedding the renderer.
  - This is the file you run for the tutorial.

---

## Reproduce from the ground up (Windows-first, works cross-platform)

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- A terminal (PowerShell is fine)

### 1) Get the code

Clone/download the repository into a folder like:

- `C:\Work\ML\CS340\`

### 2) Create a virtual environment

From the repo root:

```bash
py -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

(If you’re on macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`.)

### 3) Install dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

This installs:
- **PyQt6**: GUI + embedded 2D graphics
- **ursina**: included in requirements (other project graphics experiments live under `Graphics/`, but the Lang GUI renderer uses PyQt6)

### 4) Run the GUI (this is the main entry point)

From the repo root:

```bash
python LangDesgnAssignment2/ChatGPTGUI.py
```

You should see a window with:
- **Program** editor (left/top)
- **Output** console (left/bottom)
- **Graphics** panel (right)
- Buttons: **Execute Line**, **Compile All**, **Run Graphics**, **Load File**, **Clear All**

### 5) Load a demo script

In the GUI:
- click **Load File**
- open one of: `Lang/demo-ear/*.ear`
- then click **Compile All** (text-only) or **Run Graphics** (graphics-enabled)

---

## How execution works (end-to-end data flow)

This is the “big picture” call path you can narrate:

1. **GUI reads source text** from the editor (`QTextEdit.toPlainText()`).
2. The GUI creates/uses one `Interpreter` instance.
3. For batch runs (Compile All / Run Graphics), the GUI calls:
   - `Interpreter.reset_session()`
   - `Interpreter.process_source_with_blocks(source_text)`
4. Inside the interpreter:
   - each line is tokenized via `Tokenizer.tokenize_line()`
   - the token stream is encoded by `Encoder.encode_tokens()`
   - then the line is executed (statements, expressions, control-flow, function defs/calls)
5. The GUI prints:
   - the interpreter’s verbose “display lines” (trace)
   - then a `[console]` section for user-visible program output
6. For graphics runs:
   - the GUI resets the global renderer, re-attaches it to the GUI’s `QGraphicsView`, then executes code
   - if `setup()` exists, the GUI calls it
   - if `Renderer.init(...)` was called by the script, the GUI starts an animation loop
   - if `update()` exists, the GUI calls it every frame

---

## The language runtime (technical, module by module)

### `Tokenizer.py` (lexing)

- **Goal**: convert a single line of source into tokens.
- **Comments**: anything after `#` is treated as a comment and removed.
- **Tokenization**: a regex-based scanner that recognizes:
  - multi-character operators (e.g., `>=`, `<=`, `==`, `!=`, etc.)
  - numbers
  - identifiers
  - string literals (quoted)
  - single-character delimiters/operators

**Why it matters**: every other phase depends on tokens being consistent (especially for function headers, renderer calls, and expression evaluation).

### `Encoder.py` (integer code mapping)

- **Goal**: convert each token into an integer code and maintain tables.
- **Stateful per session**:
  - symbol table (identifier → code)
  - literal table (integer → code)
  - program code stream (the sequence of encoded tokens)

**Encoding ranges** (current implementation):
- Keywords: **100–199**
- Operators/Delimiters: **200–299**
- Symbols (identifiers): **600+**
- Integer literals: **900+**

**Important behavior**:
- The first time an identifier/literal is seen, it is assigned the next available code.
- The interpreter (and GUI) can print these tables and the program code stream as part of the assignment output.

### `FunctionUtils.py` (functions + environments)

- Stores function definitions as:
  - function name
  - parameter names
  - body lines
- Manages an **environment stack** so function calls can have local variables.
- Implements a `ReturnValue` exception used to unwind execution when `return` is hit.

**In practice**:
- `Interpreter.process_source_with_blocks` detects `func ...:` and records the function body.
- When a call happens, the interpreter pushes a new environment, binds parameters, runs the function body, and pops the environment.

### `Interpreter.py` (execution engine)

This is the core runtime. It owns:
- `Tokenizer`
- `Encoder`
- `FunctionUtils`
- a renderer handle (`get_renderer()`)

Key responsibilities:

- **Session state**
  - `variables: Dict[str, int]`
  - `encoder` tables and program code stream
  - block parsing state for indentation-based control flow

- **Statements supported** (high level)
  - declarations (e.g., `integer x;`)
  - assignment (e.g., `x = 10;`)
  - input / print
  - `if / elif / else` blocks (indentation-based)
  - `while` loops (indentation-based)
  - user-defined `func` and `return`

- **Expressions**
  - arithmetic and comparisons are evaluated from tokens
  - function calls can appear inside expressions (the interpreter replaces call sites with their returned numeric values)

- **Renderer calls from the language**
  - recognized by the token pattern: `Renderer . <method> ( ... ) ;`
  - dispatched by `_exec_renderer_call()`

Supported renderer methods in the language:
- `Renderer.init(width, height);`
- `Renderer.background(gray);` or `Renderer.background(r, g, b);`
- `Renderer.draw(shape, xVar, yVar, ...optional kwargs...);`
- `Renderer.clear();`

**Critical detail**: in `Renderer.draw(...)`, the `xVar` and `yVar` arguments are **variable names** (identifiers), not quoted strings.

Example:

```text
integer x;
integer y;

x = 200;
y = 200;

Renderer.init(800, 450);
Renderer.background(30, 30, 40);
Renderer.draw("circle", x, y, size=25, r=255, g=200, b=50);
```

### `Renderer.py` (embedded PyQt6 graphics)

- The renderer is a singleton (`get_renderer()`) so the interpreter and GUI can share it.
- The GUI provides a `QGraphicsView`; the renderer creates and owns the `QGraphicsScene`.

Shape model:
- `draw(...)` creates a shape item:
  - circle: `QGraphicsEllipseItem`
  - rectangle: `QGraphicsRectItem`
  - line: `QGraphicsLineItem`
- Each shape stores:
  - type
  - which Lang variables represent its coordinates
  - optional size/color parameters

Animation model:
- `start_animation(variables_dict, update_callback)` starts a `QTimer` (~60 FPS).
- Each tick:
  - the callback can mutate Lang variables (this is how `update()` drives animation)
  - `_update_shapes()` reads the current variable values and moves the shape items

---

## How the GUI is built and how it drives everything (`ChatGPTGUI.py`)

### Import strategy

The GUI lives in `LangDesgnAssignment2/`, but it imports runtime code from `Lang/` by inserting the path at runtime:

- `sys.path.insert(0, .../Lang)`
- then `from Interpreter import Interpreter`
- and `from Renderer import get_renderer, reset_renderer`

This is why you run the GUI from the repo root without packaging the project.

### UI layout

- A main horizontal splitter:
  - left: program editor + output console
  - right: graphics view

### The three execution buttons (the ones to focus on in the tutorial)

- **Execute Line**
  - finds the line under the cursor
  - calls `Interpreter.process_line(line)`

- **Compile All**
  - resets the session (`reset_session`)
  - executes the whole editor text using `process_source_with_blocks`
  - prints trace output plus `[console]` outputs

- **Run Graphics**
  - clears output
  - `reset_renderer()` + `interpreter.reset_session()`
  - reconnects renderer to the GUI’s `QGraphicsView`
  - executes the script (`process_source_with_blocks`)
  - calls `setup()` if defined
  - if `Renderer.init(...)` was called, starts the animation loop
  - if `update()` is defined, calls it once per frame

This “setup/update” pattern is what you’ll demonstrate for animation.

---

## A minimal graphics demo script (for your video)

Paste into the Program editor and click **Run Graphics**:

```text
integer x;
integer y;
integer dx;

x = 100;
y = 225;
dx = 4;

func setup():
    Renderer.init(800, 450);
    Renderer.background(30, 30, 40);
    Renderer.draw("circle", x, y, size=25, r=255, g=200, b=50);

func update():
    x = x + dx;
    if x > 775:
        dx = -4;
    elif x < 25:
        dx = 4;
```

What to narrate:
- declarations establish variables
- `setup()` creates the scene and draws a circle bound to `x` and `y`
- `update()` changes `x` every frame, and the renderer moves the circle because it reads `variables[x]` continuously

---

## Troubleshooting (common issues)

- **GUI opens but graphics stays blank**
  - Ensure the script calls `Renderer.init(...)` inside `setup()` or top-level code.

- **Shape draws but never moves**
  - Ensure `update()` exists and modifies the same variables you used in `Renderer.draw("circle", x, y, ...)`.
  - Ensure you passed identifiers (`x`, `y`), not quoted strings (`"x"`, `"y"`).

- **PyQt6 install/runtime errors**
  - Recreate the venv and reinstall requirements.
  - On Windows, ensure you’re running inside the activated `.venv`.

---

## Extending the project (what to say if you discuss design)

- **Add new language features**: update tokenization patterns in `Tokenizer.py`, add codes in `Encoder.py`, then implement execution in `Interpreter.py`.
- **Add new renderer methods**: implement the method in `Renderer.py`, then add a dispatch case in `Interpreter._exec_renderer_call`.
- **Improve correctness**: replace “pythonic expression evaluation” with a real expression parser (AST) if extending beyond the assignment.
