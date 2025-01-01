import sys
import tempfile
import os
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import QTimer, Qt


class MultiSearch(QWidget):
    def __init__(self):
        super().__init__()

        try:
            # Temporary files for current lines and executed lines
            self.temp_current_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8')
            self.temp_executed_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8')
        except Exception as e:
            self.show_error_message(f"Failed to create temporary files: {e}")
            sys.exit(1)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Multi-Searching')
        self.setGeometry(300, 300, 500, 400)

        # Buttons for search and "run all"
        self.run_button = QPushButton('Search', self)
        self.run_button.clicked.connect(self.run_script)
        self.run_button.setCursor(Qt.PointingHandCursor)

        self.all_run_button = QPushButton('Search All Again', self)
        self.all_run_button.clicked.connect(self.run_all_scripts)
        self.all_run_button.setCursor(Qt.PointingHandCursor)

        self.update_buttons()

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText('Add what you wish to search line by line...')
        self.text_edit.setStyleSheet('color: #00FF00;')  # Green text for the editor
        self.text_edit.textChanged.connect(self.update_query_count)  # Connect to update count on text change

        # Label for query count display
        self.query_count_label = QLabel('0/15', self)
        self.query_count_label.setStyleSheet('color: white; font-size: 14px;')

        # Label for the additional message
        self.message_label = QLabel('', self)  # Empty initially
        self.message_label.setStyleSheet('color: yellow; font-size: 14px;')  # Yellow message text

        self.footer_label = QLabel('<a href="https://www.linkedin.com/in/samraat-jain/" style="color:white; text-decoration:none;">Created by Samraat Jain</a>', self)
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setStyleSheet('color: white; font-size: 14px;')
        self.footer_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.query_count_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.run_button)
        layout.addWidget(self.all_run_button)
        layout.addWidget(self.footer_label)

        self.setLayout(layout)

        # Apply dark theme to the entire window
        self.apply_dark_theme()

        # Ensure editor is empty on start
        self.text_edit.clear()

    def apply_dark_theme(self):
        """Apply a dark theme with green text and minimalistic design."""
        dark_style = """
            QWidget {
                background-color: #121212;
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                font-size: 16px;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QTextEdit {
                background-color: #121212;
                color: #00FF00;  /* Matrix green text */
                font-family: "Courier New", Courier, monospace;
                font-size: 20px;
            }
            QTextEdit:focus {
                border: 2px solid #00FF00;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """
        self.setStyleSheet(dark_style)

    def update_buttons(self):
        self.run_button.setEnabled(True)
        self.all_run_button.setEnabled(True)

    def update_query_count(self):
        """Update the query count label and ensure no more than 15 lines."""
        try:
            lines = self.text_edit.toPlainText().splitlines()
            count = len([line for line in lines if line.strip()])  # Count non-empty lines
            self.query_count_label.setText(f'{count}/15')

            # If more than 15 lines, show a message and prevent further input beyond 15
            if count > 15:
                # Display the message
                self.message_label.setText('Maximum of 15 queries allowed for optimal usage.')
                self.message_label.setStyleSheet('color: yellow; font-size: 18px;')
                # Truncate to 15 lines
                self.text_edit.setPlainText("\n".join(lines[:15]))
                self.text_edit.setReadOnly(False)  # Allow editing of previous queries

                # Hide the message after 3 seconds
                QTimer.singleShot(3000, self.clear_message)
        except Exception as e:
            self.show_error_message(f"Failed to update query count: {e}")

    def clear_message(self):
        """Clear the message label."""
        self.message_label.setText('')

    def perform_search(self, query):
        """Perform a web search using the default browser."""
        try:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
        except Exception as e:
            self.show_error_message(f"Failed to perform search: {e}")

    def run_script(self):
        try:
            # Save current content of the text editor to the temporary current file
            content = self.text_edit.toPlainText()
            self.temp_current_file.seek(0)
            self.temp_current_file.truncate()
            self.temp_current_file.write(content)
            self.temp_current_file.flush()

            # Get the current lines
            current_lines = content.splitlines()

            # Get previously executed lines
            self.temp_executed_file.seek(0)
            executed_lines = set(self.temp_executed_file.read().splitlines())

            # Find new lines
            new_lines = [line for line in current_lines if line.strip() and line not in executed_lines]

            # Execute new lines
            for line in new_lines:
                print(f"Executing query: {line}")
                self.perform_search(line)  # Use the webbrowser-based search method

            # Update the executed lines file
            self.temp_executed_file.seek(0)
            self.temp_executed_file.truncate()
            self.temp_executed_file.write('\n'.join(current_lines))
            self.temp_executed_file.flush()
        except Exception as e:
            self.show_error_message(f"Failed to execute the script: {e}")

    def run_all_scripts(self):
        try:
            content = self.text_edit.toPlainText()
            self.temp_current_file.seek(0)
            self.temp_current_file.truncate()
            self.temp_current_file.write(content)
            self.temp_current_file.flush()

            # Get the current lines
            current_lines = content.splitlines()

            for line in current_lines:
                print(f"Executing query: {line}")
                self.perform_search(line)
        except Exception as e:
            self.show_error_message(f"Failed to execute all scripts: {e}")

    def closeEvent(self, event):
        """Override close event to clean up temporary files before the app closes."""
        try:
            self.temp_current_file.close()
            self.temp_executed_file.close()
            os.unlink(self.temp_current_file.name)
            os.unlink(self.temp_executed_file.name)
        except Exception as e:
            self.show_error_message(f"Failed to clean up temporary files: {e}")
        finally:
            event.accept()

    def show_error_message(self, message):
        """Display an error message to the user."""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle('Error')
        error_box.setText(message)
        error_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiSearch()
    window.show()
    sys.exit(app.exec_())
