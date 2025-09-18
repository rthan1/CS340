'''
/*******************************************************************
*                     GUI for Compiler of EAR                      *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 9/4/25                                                  *
*    REQUIREMENT: Assignment number 2                              *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Contains the code for the graphical aspect of the complier    *
*    Contains three boxes one for code, output, and graphics       *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
'''

import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSplitter
)
from PyQt6.QtCore import Qt

class CodeRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Code Runner")
        self.setGeometry(100, 100, 1000, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Split main area ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Program (text input) ---
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("# Type your Python code here")
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
        self.graphics_box.setPlaceholderText("Graphics will appear here if your code opens a window.")
        splitter.addWidget(self.wrap_with_label("Graphics", self.graphics_box))

        splitter.setSizes([350, 350, 300])  # initial size distribution
        main_layout.addWidget(splitter)

        # --- Run button ---
        run_button = QPushButton("Run Code")
        run_button.setStyleSheet("""
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
        run_button.clicked.connect(self.run_code)
        main_layout.addWidget(run_button)

    def wrap_with_label(self, title, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 15px;")
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def run_code(self):
        code = self.code_editor.toPlainText()
        self.output_box.clear()

        # Run code in a subprocess to isolate environment
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout:
                self.output_box.append(result.stdout)
            if result.stderr:
                self.output_box.append(result.stderr)
        except Exception as e:
            self.output_box.append(f"Error running code: {e}")

def main():
    app = QApplication(sys.argv)
    window = CodeRunner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()