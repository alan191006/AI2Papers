import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import json

class LabelingApp(QWidget):
    def __init__(self, data_file):
        super().__init__()

        # Load JSON data
        with open(data_file, "r") as json_file:
            self.data = json.load(json_file)
            
        self.data_file = data_file

        self.current_index = self.find_next_unlabeled_entry()

        # UI components
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)  # Center-align text
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))  # Set font size

        self.abstract_browser = QTextBrowser()
        self.abstract_browser.setFont(QFont("Arial", 14))  # Set font size

        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")

        # Connect buttons to actions
        self.yes_button.clicked.connect(self.label_entry_yes)
        self.no_button.clicked.connect(self.label_entry_no)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.abstract_browser)
        layout.addWidget(self.yes_button)
        layout.addWidget(self.no_button)

        self.setLayout(layout)

        # Initialize UI
        self.update_ui()

    def find_next_unlabeled_entry(self):
        for idx, entry in enumerate(self.data):
            if "label" not in entry:
                return idx
        return -1  # All entries labeled

    def update_ui(self):
        if self.current_index == -1:
            self.title_label.setText("All entries labeled.")
            self.abstract_browser.clear()
            self.yes_button.setEnabled(False)
            self.no_button.setEnabled(False)
        else:
            entry = self.data[self.current_index]
            self.title_label.setText(entry["title"])
            self.abstract_browser.setPlainText(entry["abstract"])
            self.yes_button.setEnabled(True)
            self.no_button.setEnabled(True)

    def label_entry_yes(self):
        self.label_entry(1)

    def label_entry_no(self):
        self.label_entry(0)

    def label_entry(self, label_value):
        if 0 <= self.current_index < len(self.data):
            self.data[self.current_index]["label"] = label_value
            self.current_index = self.find_next_unlabeled_entry()
            self.update_ui()

    def closeEvent(self, event):
        # Write changes to the JSON file before closing the application
        with open(self.data_file.replace(".json", "_edited.json"), "w") as json_file:
            json.dump(self.data, json_file, indent=2)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelingApp("data\data_30-01-2024_mr_2000.json")
    window.show()
    sys.exit(app.exec_())
