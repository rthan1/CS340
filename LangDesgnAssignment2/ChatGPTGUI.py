'''
/*******************************************************************
*                     GUI for Compiler of EAR                      *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 9/4/25                                                  *
*    REQUIREMENT: Assignment number 3                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Contains the code for the graphical aspect of the complier    *
*    Contains three boxes one for code, output, and graphics       *
*    Modified for Assignment 3: Tokenization implementation        *
*    Displays line numbers and tokenized output with eol/eof       *
*    Updated: Added 2D Renderer support with QGraphicsView         *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
'''

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSplitter, QFileDialog,
    QGraphicsView, QGraphicsScene
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

# Add parent directory to path to import from Lang
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Lang'))
from Interpreter import Interpreter
from Renderer import get_renderer, reset_renderer

class CodeRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EAR Programming Language - Interactive IDE")
        self.setGeometry(100, 100, 1200, 800)
        # Enable verbose mode so tokens, code generators, and console outputs are shown
        self.interpreter = Interpreter(verbose=True)
        self.init_ui()
        self._setup_renderer()

    def _setup_renderer(self):
        """Connect the renderer to the graphics view."""
        renderer = get_renderer()
        renderer.set_view(self.graphics_view)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Main horizontal splitter (code/output on left, graphics on right) ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left side: code and output stacked vertically ---
        left_splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Program (text input) ---
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText(
            "# Type your EAR code here\n"
            "# Click 'Execute Line' to execute current line\n"
            "# Click 'Compile All' to compile all lines\n"
            "# Click 'Run Graphics' to run with 2D renderer\n"
            "# Load .ear scripts via 'Load File'"
        )
        self.code_editor.setStyleSheet("font-family: Consolas; font-size: 14px;")
        left_splitter.addWidget(self.wrap_with_label("Program", self.code_editor))

        # --- Output box ---
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("font-family: Consolas; font-size: 13px; color: white; background-color: black;")
        left_splitter.addWidget(self.wrap_with_label("Output", self.output_box))

        left_splitter.setSizes([400, 300])
        main_splitter.addWidget(left_splitter)

        # --- Graphics view (landscape, larger) ---
        self.graphics_view = QGraphicsView()
        self.graphics_view.setMinimumSize(600, 400)
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                background-color: #1e1e28;
                border: 2px solid #3a3a4a;
                border-radius: 4px;
            }
        """)
        # Initialize with empty scene
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 800, 450)
        scene.setBackgroundBrush(QBrush(QColor(30, 30, 40)))
        self.graphics_view.setScene(scene)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_splitter.addWidget(self.wrap_with_label("Graphics (800x450 Landscape)", self.graphics_view))

        main_splitter.setSizes([500, 700])  # Give more space to graphics
        main_layout.addWidget(main_splitter)

        # --- Button layout ---
        button_layout = QHBoxLayout()
        
        # Execute Line button
        execute_line_button = QPushButton("Execute Line")
        execute_line_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #28a745;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        execute_line_button.clicked.connect(self.execute_line)
        button_layout.addWidget(execute_line_button)
        
        # Compile All button
        compile_button = QPushButton("Compile All")
        compile_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #0078D7;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        compile_button.clicked.connect(self.compile_code)
        button_layout.addWidget(compile_button)

        # Run Graphics button
        run_graphics_button = QPushButton("Run Graphics")
        run_graphics_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #9b59b6;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        run_graphics_button.clicked.connect(self.run_graphics)
        button_layout.addWidget(run_graphics_button)
        
        # Load File button
        load_file_button = QPushButton("Load File")
        load_file_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #6c757d;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        load_file_button.clicked.connect(self.load_file)
        button_layout.addWidget(load_file_button)
        
        # Clear button
        clear_button = QPushButton("Clear All")
        clear_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #dc3545;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_button)
        
        main_layout.addLayout(button_layout)

    def wrap_with_label(self, title, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 15px;")
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def _execute_all_text(self, code: str, header: str):
        """
        Execute all non-empty lines of the given code text using the Interpreter.
        Uses the new process_source_with_blocks for control flow support.
        """
        self.output_box.append(header)
        self.output_box.append("-" * 60)

        # Start a fresh session for the batch execution
        self.interpreter.reset_session()

        try:
            display_lines, all_outputs = self.interpreter.process_source_with_blocks(code)
            
            for msg in display_lines:
                self.output_box.append(msg)

            self.output_box.append("-" * 60)
            self.output_box.append(f"[EXECUTION COMPLETE]")

            # After the verbose trace, show a [console] section with the plain
            # program output in execution order.
            if all_outputs:
                self.output_box.append("[console]")
                for val in all_outputs:
                    self.output_box.append(str(val))
        except Exception as e:
            self.output_box.append(f"Error: {e}")

        self.output_box.append("")

    def run_graphics(self):
        """
        Run the code with graphics/renderer support.
        Calls setup() function if defined and starts animation.
        """
        self.output_box.clear()
        code = self.code_editor.toPlainText()
        
        if not code.strip():
            self.output_box.append("No code to run.\n")
            return

        self.output_box.append("[RUNNING GRAPHICS]")
        self.output_box.append("-" * 60)

        # Reset renderer and interpreter for fresh run
        reset_renderer()
        self.interpreter.reset_session()
        
        # Reconnect renderer to the view
        renderer = get_renderer()
        renderer.set_view(self.graphics_view)

        try:
            # Process the source to define functions and execute setup code
            display_lines, all_outputs = self.interpreter.process_source_with_blocks(code)
            
            for msg in display_lines:
                self.output_box.append(msg)

            # Call setup() if defined
            if self.interpreter.func_utils.has_function('setup'):
                self.output_box.append("[Calling setup() function]")
                try:
                    _, setup_outputs = self.interpreter._call_function('setup', [])
                    all_outputs.extend(setup_outputs)
                except Exception as e:
                    self.output_box.append(f"Error in setup(): {e}")
                    return

            # If renderer was initialized, start animation
            if renderer.is_initialized():
                self.output_box.append("[Renderer initialized - starting animation]")
                
                # Create update callback that calls update() function each frame
                def frame_update():
                    if self.interpreter.func_utils.has_function('update'):
                        try:
                            self.interpreter._call_function('update', [])
                        except Exception:
                            pass  # Silently handle errors in update loop
                
                # Check if update() is defined
                if self.interpreter.func_utils.has_function('update'):
                    self.output_box.append("[update() function defined - will animate each frame]")
                    renderer.start_animation(self.interpreter.variables, frame_update)
                else:
                    self.output_box.append("[No update() function - static display]")
                    renderer.start_animation(self.interpreter.variables)
                
                # Fit the view to show the scene properly
                self.graphics_view.fitInView(
                    renderer.scene.sceneRect(), 
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            else:
                self.output_box.append("[No Renderer.init() called - graphics not started]")

            self.output_box.append("-" * 60)
            self.output_box.append("[GRAPHICS RUNNING]")

            if all_outputs:
                self.output_box.append("[console]")
                for val in all_outputs:
                    self.output_box.append(str(val))

        except Exception as e:
            self.output_box.append(f"Error: {e}")

        self.output_box.append("")

    def execute_line(self):
        self.output_box.clear()
        """
        Execute the current line where the cursor is positioned
        """
        cursor = self.code_editor.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        line = cursor.selectedText().strip()
        
        if not line:
            self.output_box.append("No line to execute.\n")
            return
        
        line_no, display_lines, _, print_outputs = self.interpreter.process_line(line)
        self.output_box.append(f"{line_no}. {line}")
        for msg in display_lines:
            self.output_box.append(msg)

        if print_outputs:
            self.output_box.append("[console]")
            for val in print_outputs:
                self.output_box.append(str(val))

        self.output_box.append("")

    def compile_code(self):
        self.output_box.clear()
        """
        Compile all lines in the code editor using the Interpreter
        """
        code = self.code_editor.toPlainText()
        
        if not code.strip():
            self.output_box.append("No code to compile.\n")
            return
        # Use the same execution/verbose path as Execute Line, but for all lines
        self._execute_all_text(code, "[EXECUTING] All Code")

    def load_file(self):
        """
        Load a file into the code editor and compile it via Interpreter
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "EAR Scripts (*.ear);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                
                self.code_editor.setPlainText(content)
                # Execute the loaded file using the same path as Compile All
                self.output_box.clear()
                self.output_box.append(f"[LOADED FILE] {os.path.basename(file_path)}")
                self._execute_all_text(content, "[EXECUTING] Loaded Code")
                
            except Exception as e:
                self.output_box.append(f"Error loading file: {e}\n")

    def clear_all(self):
        """Clear the output box and reset graphics."""
        self.output_box.clear()
        reset_renderer()
        self._setup_renderer()
        # Reset scene to default
        scene = self.graphics_view.scene()
        if scene:
            scene.clear()
            scene.setBackgroundBrush(QBrush(QColor(30, 30, 40)))

def main():
    app = QApplication(sys.argv)
    window = CodeRunner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
