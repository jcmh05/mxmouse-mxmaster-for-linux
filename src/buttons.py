from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CircularButton(QPushButton):
    def __init__(self, name, parent=None):
        super().__init__('', parent)
        self.name = name
        self.selected = False
        self.setFixedSize(40, 40)
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2C3E50;
                    border: 3px solid #2980b9;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #34495E;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 3px solid #FFFFFF;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
