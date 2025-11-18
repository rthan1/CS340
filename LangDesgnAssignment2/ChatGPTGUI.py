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
    QTextEdit, QPushButton, QLabel, QSplitter, QFileDialog
)
from PyQt6.QtCore import Qt

# Add parent directory to path to import from Lang
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Lang'))
from Interpreter import Interpreter

class CodeRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lang Programming Language - Interactive IDE")
        self.setGeometry(100, 100, 1000, 600)
        # Enable verbose mode so tokens, code generators, and console outputs are shown
        self.interpreter = Interpreter(verbose=True)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Split main area ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Program (text input) ---
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("# Type your Lang code here\n# Click 'Execute Line' to execute current line\n# Click 'Compile All' to compile all lines")
        self.code_editor.setStyleSheet("font-family: Consolas; font-size: 14px;")
        splitter.addWidget(self.wrap_with_label("Program", self.code_editor))

        # --- Output box ---
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("font-family: Consolas; font-size: 13px; color: white; background-color: black;")
        splitter.addWidget(self.wrap_with_label("Output", self.output_box))

        # --- Graphics box ---
        self.graphics_box = QTextEdit()
        self.graphics_box.setReadOnly(True)
        self.graphics_box.setStyleSheet("font-family: Consolas; font-size: 13px; background-color: #f0f0f0;")
        self.graphics_box.setPlaceholderText("Graphics will appear here in future assignments.")
        splitter.addWidget(self.wrap_with_label("Graphics", self.graphics_box))

        splitter.setSizes([350, 350, 300])  # initial size distribution
        main_layout.addWidget(splitter)

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
        clear_button = QPushButton("Clear Output")
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
        clear_button.clicked.connect(self.clear_output)
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
        Uses the same semantics as 'Execute Line', including verbose output and
        console outputs from print statements.
        """
        self.output_box.append(header)
        self.output_box.append("-" * 60)

        # Start a fresh session for the batch execution
        self.interpreter.reset_session()

        processed = 0
        all_outputs: list[int] = []
        lines = code.split('\n')
        for original in lines:
            line = original.strip()
            if not line:
                continue
            processed += 1
            try:
                line_no, display_lines, _, print_outputs = self.interpreter.process_line(line)
                self.output_box.append(f"{line_no}. {line}")
                for msg in display_lines:
                    self.output_box.append(msg)
                self.output_box.append("")
                all_outputs.extend(print_outputs)
            except Exception as e:
                self.output_box.append(f"Error on line {line_no}: {e}")
                self.output_box.append("")
                break

        self.output_box.append("-" * 60)
        self.output_box.append(f"[EXECUTION COMPLETE] Processed {processed} line(s)")

        # After the verbose trace, show a [console] section with the plain
        # program output in execution order.
        if all_outputs:
            self.output_box.append("[console]")
            for val in all_outputs:
                self.output_box.append(str(val))

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
            "Text Files (*.txt);;All Files (*.*)"
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

    def clear_output(self):
        """Clear the output box"""
        self.output_box.clear()

def main():
    app = QApplication(sys.argv)
    window = CodeRunner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()