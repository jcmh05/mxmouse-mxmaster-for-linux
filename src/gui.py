import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QComboBox, QLineEdit, 
    QRadioButton, QButtonGroup, QSystemTrayIcon, QMenu, QAction,
    QCheckBox, QSlider, QVBoxLayout, QHBoxLayout, QFrame, QApplication
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from src.buttons import CircularButton
from src.buttons_info import buttons_info
from src.utils import resource_path

MAX_ACTION_LABEL_LENGTH = 15

class Communicate(QObject):
    update_battery = pyqtSignal(int)

class MainWindow(QMainWindow):
    action_changed = pyqtSignal(str, str)  # button_name, action

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.comm = Communicate()
        self.comm.update_battery.connect(self.update_battery_status)

        self.setWindowTitle("Logitech MX Master Configurator")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")

        # Icono de la app
        app_icon_path = resource_path(os.path.join('assets', 'app_icon.png'))
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        else:
            print("App icon not found. Using default icon.")

        self.selected_button = None
        self.battery_percentage = 75

        # Layout principal
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Encabezado
        header = QFrame()
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header.setFixedHeight(150)
        header.setStyleSheet("background-color: #F1F1F1;")

        # Nombre del Ratón
        name_label = QLabel("MX Master 3S")
        name_label.setFont(QFont('Arial', 24, QFont.Bold))
        name_label.setStyleSheet("color: #34495E;")
        name_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(name_label)

        # Indicador de Batería
        battery_layout = QHBoxLayout()
        battery_layout.setAlignment(Qt.AlignCenter)
        header_layout.addLayout(battery_layout)

        self.battery_label = QLabel()
        self.battery_label.setFixedSize(96, 24)
        battery_layout.addWidget(self.battery_label)

        self.battery_percentage_label = QLabel(f"{self.battery_percentage}%")
        self.battery_percentage_label.setFont(QFont('Arial', 12))
        self.battery_percentage_label.setStyleSheet("color: #2C3E50;")
        battery_layout.addWidget(self.battery_percentage_label)

        main_layout.addWidget(header)

        # Cuerpo principal
        body = QHBoxLayout()
        main_layout.addLayout(body)

        # Panel Izquierdo
        left_panel = QFrame()
        left_panel.setFixedWidth(320)
        left_panel.setStyleSheet("background-color: #F9F9F9; border-right: 1px solid #DDDDDD;")
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        actions_title = QLabel("Actions")
        actions_title.setFont(QFont('Arial', 18, QFont.Bold))
        actions_title.setStyleSheet("color: #2C3E50; margin-top:10px; margin-left:10px;")
        left_layout.addWidget(actions_title, alignment=Qt.AlignTop | Qt.AlignLeft)

        self.action_command_group = QButtonGroup(self)
        self.action_radio = QRadioButton("Select Action")
        self.command_radio = QRadioButton("Custom Command")
        self.action_command_group.addButton(self.action_radio)
        self.action_command_group.addButton(self.command_radio)

        radio_layout = QVBoxLayout()
        radio_layout.setSpacing(10)
        radio_layout.addWidget(self.action_radio)

        dropdown_arrow_path = resource_path(os.path.join('assets', 'dropdown_arrow.png'))
        switch_off_path = resource_path(os.path.join('assets', 'switch_off.png'))
        switch_on_path = resource_path(os.path.join('assets', 'switch_on.png'))
        mouse_pixmap_path = resource_path(os.path.join('assets', 'mouse.png'))

        self.action_dropdown = QComboBox()
        self.action_dropdown.addItems([
            "Copy", "Paste", "Volume Up", "Volume Down", "Mute", "Undo", "Redo",
            "Scroll Up", "Scroll Down", "Scroll Left", "Scroll Right",
            "Left Click", "Right Click", "Forward", "Back",
            "Open Terminal", "Show Desktop", "Close Window",
        ])
        self.action_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 4px;
            }}
            QComboBox::drop-down {{
                border-left-width: 1px;
                border-left-color: #CCCCCC;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url('{dropdown_arrow_path}');
                width: 10px;
                height: 10px;
            }}
        """)
        self.action_dropdown.setEnabled(False)
        self.action_dropdown.currentIndexChanged.connect(self.on_action_change)
        radio_layout.addWidget(self.action_dropdown)

        radio_layout.addWidget(self.command_radio)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter custom command")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:disabled {
                background-color: #EEEEEE;
                color: #AAAAAA;
            }
        """)
        self.command_input.setEnabled(False)
        self.command_input.textChanged.connect(self.on_command_change)
        radio_layout.addWidget(self.command_input)

        left_layout.addLayout(radio_layout)
        self.action_radio.toggled.connect(self.on_radio_toggle)
        self.command_radio.toggled.connect(self.on_radio_toggle)

        # Gestures
        self.gestures_switch = QCheckBox("Enable Gestures")
        self.gestures_switch.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
            }}
            QCheckBox::indicator {{
                width: 40px; 
                height: 40px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url('{switch_off_path}');
            }}
            QCheckBox::indicator:checked {{
                image: url('{switch_on_path}');
            }}
        """)
        self.gestures_switch.hide()
        self.gestures_switch.stateChanged.connect(self.on_gestures_switch_toggle)
        left_layout.addWidget(self.gestures_switch)

        self.gesture_actions = [
            "No Action", "Custom Command",
            "Copy", "Paste", "Volume Up", "Volume Down", "Mute",
            "Undo", "Redo", "Scroll Up", "Scroll Down",
            "Left Click", "Right Click", "Open Terminal", "Lock Screen", "Show Desktop"
        ]

        self.gesture_labels = {}
        self.gesture_combos = {}
        self.gesture_command_inputs = {}

        directions = ["Up", "Down", "Left", "Right"]
        for direction in directions:
            label = QLabel(f"{direction}:")
            label.setStyleSheet("font-size: 14px; margin-top:5px;")
            label.hide()
            combo = QComboBox()
            combo.addItems(self.gesture_actions)
            combo.hide()
            combo.currentIndexChanged.connect(self.on_gesture_combo_changed)

            command_input = QLineEdit()
            command_input.setPlaceholderText("Enter custom command for gesture")
            command_input.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLineEdit:disabled {
                    background-color: #EEEEEE;
                    color: #AAAAAA;
                }
            """)
            command_input.hide()
            command_input.textChanged.connect(lambda txt, dir_=direction.lower(): self.on_gesture_command_changed(dir_, txt))

            left_layout.addWidget(label)
            left_layout.addWidget(combo)
            left_layout.addWidget(command_input)  # Lo añadimos debajo del combo

            self.gesture_labels[direction.lower()] = label
            self.gesture_combos[direction.lower()] = combo
            self.gesture_command_inputs[direction.lower()] = command_input

        self.inversion_checkbox = QCheckBox("Invert Scroll")
        self.inversion_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
            }}
            QCheckBox::indicator {{
                width: 40px; 
                height: 40px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url('{switch_off_path}');
            }}
            QCheckBox::indicator:checked {{
                image: url('{switch_on_path}');
            }}
        """)
        self.inversion_checkbox.hide()
        self.inversion_checkbox.stateChanged.connect(self.on_inversion_toggle)
        left_layout.addWidget(self.inversion_checkbox)

        func_layout = QVBoxLayout()
        self.func_label = QLabel("Functionality:")
        self.func_label.setStyleSheet("font-size:14px; margin-top:10px;")
        self.func_label.hide()
        func_layout.addWidget(self.func_label)

        self.wheel_function_combo = QComboBox()
        self.wheel_function_combo.addItems(["Scroll Horizontal", "Volume Control", "Zoom"])
        self.wheel_function_combo.setCurrentIndex(0)
        self.wheel_function_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 4px;
            }
        """)
        self.wheel_function_combo.hide()
        self.wheel_function_combo.currentIndexChanged.connect(self.on_wheel_function_change)
        func_layout.addWidget(self.wheel_function_combo)

        left_layout.addLayout(func_layout)

        self.sensitivity_label = QLabel("Sensitivity:")
        self.sensitivity_label.setStyleSheet("font-size: 14px; margin-top:5px;")
        self.sensitivity_label.hide()
        left_layout.addWidget(self.sensitivity_label)

        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(50)
        self.sensitivity_slider.setMaximum(200)
        self.sensitivity_slider.setValue(100)
        self.sensitivity_slider.setTickInterval(10)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setStyleSheet("""
            QSlider::handle:horizontal {
                background-color: #2980b9;
                border: 1px solid #5dade2;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #CCCCCC;
                margin: 0px;
                border-radius: 2px;
            }
        """)
        self.sensitivity_slider.hide()
        self.sensitivity_slider.valueChanged.connect(self.on_sensitivity_change)
        left_layout.addWidget(self.sensitivity_slider)
        left_layout.addStretch()
        body.addWidget(left_panel)

        right_panel = QFrame()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_layout.setContentsMargins(20, 20, 20, 20)

        self.mouse_pixmap = QPixmap(mouse_pixmap_path)
        self.mouse_label = QLabel()
        self.mouse_label.setPixmap(self.mouse_pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.mouse_label.setAlignment(Qt.AlignCenter)
        self.mouse_label.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 10px;")
        self.mouse_label.setFixedSize(800, 600)

        self.overlay = QWidget(self.mouse_label)
        self.overlay.setGeometry(0, 0, self.mouse_label.width(), self.mouse_label.height())
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.overlay.setStyleSheet("background: transparent;")

        self.buttons = []
        self.add_overlay_buttons()

        right_layout.addWidget(self.mouse_label, alignment=Qt.AlignCenter)
        body.addWidget(right_panel)

        self.tray_icon = QSystemTrayIcon(self)
        tray_icon_path = resource_path(os.path.join('assets', 'app_icon.png'))
        if os.path.exists(tray_icon_path):
            self.tray_icon.setIcon(QIcon(tray_icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QSystemTrayIcon.SP_ComputerIcon))

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_application)
        self.tray_icon.show()

        self.action_changed.connect(self.on_action_change)
        self.select_button("Button 1")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "MX Master Configurator",
            "La aplicación se ha minimizado a la bandeja del sistema.",
            QSystemTrayIcon.Information,
            2000
        )

    def close_application(self):
        self.config_manager.save_actions()
        QApplication.quit()

    def on_wheel_function_change(self, index):
        if self.selected_button == "Button 5":
            selected_func = self.wheel_function_combo.currentText()
            self.config_manager.set_wheel_function(selected_func)
            print(f"[Button 5] Funcionalidad seleccionada: {selected_func}")

    def on_action_change(self, index):
        if not self.selected_button:
            return

        # Se captura la posible excepción si index no es un int
        try:
            index = int(index)
        except (ValueError, TypeError):
            # Simplemente ignoramos si no es convertible a int
            return

        if self.action_radio.isChecked() and self.selected_button not in ["Button 5", "Button 1"]:
            if index >= 0:
                selected_action = self.action_dropdown.currentText()
                self.config_manager.set_action(self.selected_button, selected_action)
                self.buttons[self.get_button_index(self.selected_button)].action_label.setText(
                    self.format_action_text(selected_action)
                )
                self.action_changed.emit(self.selected_button, selected_action)

        elif self.action_radio.isChecked() and self.selected_button == "Button 1":
            if index >= 0:
                selected_action = self.action_dropdown.currentText()
                self.config_manager.set_action("Button 1", selected_action)
                self.buttons[self.get_button_index("Button 1")].action_label.setText(
                    self.format_action_text(selected_action)
                )

    def on_command_change(self, text):
        if not self.selected_button:
            return

        if self.command_radio.isChecked() and self.selected_button not in ["Button 5", "Button 1"]:
            if text:
                self.config_manager.set_action(self.selected_button, f"Command: {text}")
                self.buttons[self.get_button_index(self.selected_button)].action_label.setText(
                    self.format_action_text(text)
                )
            else:
                self.config_manager.set_action(self.selected_button, "")
                self.buttons[self.get_button_index(self.selected_button)].action_label.setText("No Action")
        elif self.command_radio.isChecked() and self.selected_button == "Button 1":
            if text:
                self.config_manager.set_action("Button 1", f"Command: {text}")
                self.buttons[self.get_button_index("Button 1")].action_label.setText(
                    self.format_action_text(text)
                )
            else:
                self.config_manager.set_action("Button 1", "")
                self.buttons[self.get_button_index("Button 1")].action_label.setText("No Action")

    def on_radio_toggle(self):
        self.action_dropdown.setEnabled(self.action_radio.isChecked())
        self.command_input.setEnabled(self.command_radio.isChecked())

    def on_gestures_switch_toggle(self, state):
        if self.selected_button == "Button 1":
            enabled = (state == Qt.Checked)
            self.config_manager.set_gestures_enabled(enabled)
            self.show_gestures_ui(enabled)
            if enabled:
                for direction, combo in self.gesture_combos.items():
                    action = self.config_manager.get_gesture_action(direction)
                    combo.setCurrentText(action if action else "No Action")
                    if action and action.startswith("Command:"):
                        combo.setCurrentText("Custom Command")
                        cmd_only = action.split("Command:")[1].strip()
                        self.gesture_command_inputs[direction].setText(cmd_only)
                        self.gesture_command_inputs[direction].show()
            else:
                for combo in self.gesture_combos.values():
                    combo.setCurrentIndex(0)
                for cmd_input in self.gesture_command_inputs.values():
                    cmd_input.hide()

    def on_gesture_command_changed(self, direction, text):
        if not self.selected_button == "Button 1":
            return
        # Guardamos en config_manager como "Command: <texto>"
        if text:
            self.config_manager.set_gesture_action(direction, f"Command: {text}")
        else:
            self.config_manager.set_gesture_action(direction, "")

    def on_gesture_combo_changed(self, index):
        if self.selected_button != "Button 1":
            return

        combo = self.sender()
        direction = None
        for dir_key, cmb in self.gesture_combos.items():
            if cmb == combo:
                direction = dir_key
                break

        if direction:
            action_selected = combo.currentText()
            if action_selected == "No Action":
                action_selected = ""
                self.gesture_command_inputs[direction].hide()
                self.config_manager.set_gesture_action(direction, action_selected)
            elif action_selected == "Custom Command":
                self.gesture_command_inputs[direction].show()
                current_cmd = self.gesture_command_inputs[direction].text()
                if current_cmd:
                    self.config_manager.set_gesture_action(direction, f"Command: {current_cmd}")
                else:
                    self.config_manager.set_gesture_action(direction, "")
            else:
                self.gesture_command_inputs[direction].hide()
                self.config_manager.set_gesture_action(direction, action_selected)

            self.update_button_label("Button 1")

    def show_gestures_ui(self, show: bool):
        for direction in self.gesture_labels.keys():
            self.gesture_labels[direction].setVisible(show)
            self.gesture_combos[direction].setVisible(show)
            self.gesture_command_inputs[direction].setVisible(False)  # Se muestra solo si "Custom Command"

    def on_inversion_toggle(self, state):
        if self.selected_button == "Button 5":
            inverted = self.inversion_checkbox.isChecked()
            self.config_manager.set_inversion(inverted)

    def on_sensitivity_change(self, value):
        if self.selected_button == "Button 5":
            self.config_manager.set_sensitivity(value)

    def on_button_click(self, button):
        for btn in self.buttons:
            btn.set_selected(False)
            btn.action_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #CCCCCC;
                    border-radius: 8px;
                    padding: 5px;
                    font-weight: normal;
                }
            """)

        button.set_selected(True)
        self.selected_button = button.name
        button.action_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 2px solid #2980b9;
                border-radius: 8px;
                padding: 5px;
                font-weight: bold;
            }
        """)

        if self.selected_button == "Button 1":
            self.gestures_switch.show()
            self.hide_button5_ui()
            gestures_enabled = self.config_manager.get_gestures_enabled()
            self.gestures_switch.setChecked(gestures_enabled)
            self.show_gestures_ui(gestures_enabled)
            if gestures_enabled:
                for direction, combo in self.gesture_combos.items():
                    action = self.config_manager.get_gesture_action(direction)
                    combo.setCurrentText(action if action else "No Action")
                    if action and action.startswith("Command:"):
                        combo.setCurrentText("Custom Command")
                        cmd_only = action.split("Command:")[1].strip()
                        self.gesture_command_inputs[direction].setText(cmd_only)
                        self.gesture_command_inputs[direction].show()
            else:
                self.load_button1_action()
        elif self.selected_button == "Button 5":
            self.gestures_switch.hide()
            self.show_gestures_ui(False)
            self.show_button5_ui()
            inverted = self.config_manager.get_inversion()
            sensitivity = self.config_manager.get_sensitivity()
            self.inversion_checkbox.setChecked(inverted)
            self.sensitivity_slider.setValue(sensitivity)
            current_func = self.config_manager.get_wheel_function()
            idx_func = self.wheel_function_combo.findText(current_func)
            if idx_func >= 0:
                self.wheel_function_combo.setCurrentIndex(idx_func)
            else:
                self.wheel_function_combo.setCurrentIndex(0)
        else:
            self.gestures_switch.hide()
            self.show_gestures_ui(False)
            self.hide_button5_ui()
            self.action_radio.show()
            self.action_dropdown.show()
            self.command_radio.show()
            self.command_input.show()

            action = self.config_manager.get_action(button.name)
            if action and isinstance(action, str) and action.startswith("Command:"):
                command = action.split("Command:")[1].strip()
                self.command_input.setText(command)
                self.command_radio.setChecked(True)
            else:
                if action:
                    idx = self.action_dropdown.findText(action)
                    if idx >= 0:
                        self.action_dropdown.setCurrentIndex(idx)
                    else:
                        self.action_dropdown.setCurrentIndex(0)
                else:
                    self.action_dropdown.setCurrentIndex(0)
                self.action_radio.setChecked(True)
                self.command_input.setText("")
                self.command_input.setEnabled(False)

    def hide_button5_ui(self):
        self.inversion_checkbox.hide()
        self.sensitivity_label.hide()
        self.sensitivity_slider.hide()
        self.func_label.hide()
        self.wheel_function_combo.hide()

    def show_button5_ui(self):
        self.inversion_checkbox.show()
        self.sensitivity_label.show()
        self.sensitivity_slider.show()
        self.func_label.show()
        self.wheel_function_combo.show()

    def load_button1_action(self):
        action = self.config_manager.get_action("Button 1")
        if isinstance(action, str):
            if action.startswith("Command:"):
                cmd = action.split("Command:")[1].strip()
                self.command_input.setText(cmd)
                self.command_radio.setChecked(True)
            else:
                idx = self.action_dropdown.findText(action)
                if idx >= 0:
                    self.action_dropdown.setCurrentIndex(idx)
                else:
                    self.action_dropdown.setCurrentIndex(0)
                self.action_radio.setChecked(True)
        else:
            self.action_dropdown.setCurrentIndex(0)
            self.command_input.setText("")
            self.action_radio.setChecked(True)
            self.command_input.setEnabled(False)

    def add_overlay_buttons(self):
        for btn_info in buttons_info:
            button = CircularButton(btn_info["name"], self.overlay)
            button.move(btn_info["x"], btn_info["y"])
            button.clicked.connect(lambda checked, b=button: self.on_button_click(b))
            self.buttons.append(button)

            if btn_info["name"] == "Button 5":
                display_text = "Scroll Settings"
            else:
                action_text = self.config_manager.get_action(btn_info["name"]) or "No Action"
                display_text = self.format_action_text(action_text)

            action_label = QLabel(display_text, self.overlay)
            action_label.setFont(QFont('Arial', 12))
            action_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #CCCCCC;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            action_label.adjustSize()

            label_x, label_y = self.calculate_label_position(
                btn_info["x"], btn_info["y"], btn_info["label_pos"]
            )
            action_label.move(label_x, label_y)
            action_label.show()
            button.action_label = action_label

    def calculate_label_position(self, btn_x, btn_y, label_pos):
        positions = {
            "top-right": (btn_x + 50, btn_y - 30),
            "top-left": (btn_x - 100, btn_y - 30),
            "bottom-right": (btn_x + 50, btn_y + 10),
            "bottom-left": (btn_x - 100, btn_y + 10),
        }
        return positions.get(label_pos, (btn_x + 50, btn_y - 30))

    def format_action_text(self, text):
        if isinstance(text, str) and text.startswith("Command:"):
            text = text[len("Command:"):].strip()
        if isinstance(text, str) and len(text) > MAX_ACTION_LABEL_LENGTH:
            return text[:MAX_ACTION_LABEL_LENGTH - 3] + "..."
        return text if isinstance(text, str) else "No Action"

    def get_button_index(self, button_name):
        for index, btn in enumerate(self.buttons):
            if btn.name == button_name:
                return index
        return -1

    def update_battery_icon(self, percentage):
        level = min(max(int(percentage / 100 * 6), 0), 6)
        battery_image_path = resource_path(os.path.join('assets', f"battery_{level}.png"))
        if os.path.exists(battery_image_path):
            battery_image = QPixmap(battery_image_path)
            self.battery_label.setPixmap(
                battery_image.scaled(
                    self.battery_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
            )
        else:
            self.battery_label.setText("Battery Icon Missing")
            self.battery_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        self.battery_percentage_label.setText(f"{percentage}%")

    def update_battery_status(self, percentage):
        self.update_battery_icon(percentage)

    def update_button_label(self, button_name):
        btn_index = self.get_button_index(button_name)
        if btn_index >= 0:
            if button_name == "Button 1":
                action_text = self.config_manager.get_action("Button 1") or "No Action"
                if self.config_manager.get_gestures_enabled():
                    gestures = ["up", "down", "left", "right"]
                    for direction in gestures:
                        gesture_action = self.config_manager.get_gesture_action(direction)
                        if gesture_action:
                            action_text += f"\n{direction.title()}: {self.format_action_text(gesture_action)}"
            elif button_name == "Button 5":
                action_text = "Scroll Settings"
            else:
                action_text = self.config_manager.get_action(button_name) or "No Action"
                action_text = self.format_action_text(action_text)
            self.buttons[btn_index].action_label.setText(action_text)

    def select_button(self, button_name):
        for btn in self.buttons:
            if btn.name == button_name:
                self.on_button_click(btn)
                break
