import json
import os

def get_config_path():
    """
    Retorna la ruta donde se almacenará el archivo de configuración.
    Se utiliza el directorio del usuario (~/.mxmaster3s).
    """
    home = os.path.expanduser("~")
    config_dir = os.path.join(home, ".mxmaster3s")
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except Exception as e:
            print(f"Error al crear el directorio de configuración: {e}")
    return os.path.join(config_dir, "actions.json")

ACTIONS_FILE = get_config_path()

class ConfigManager:
    def __init__(self):
        self.actions = self.load_actions()

    def load_actions(self):
        if not os.path.exists(ACTIONS_FILE):
            # Inicializar con acciones por defecto
            default_actions = {
                "Button 1": {
                    "action": "",
                    "gestures_enabled": False,
                    "gesture_up": "",
                    "gesture_down": "",
                    "gesture_left": "",
                    "gesture_right": ""
                },
                "Button 2": "",
                "Button 3": "",
                "Button 4": "",
                "Button 5": {
                    "inverted": False,
                    "sensitivity": 100,
                    "function": "Scroll Horizontal"
                },
                "Button 6": ""
            }
            with open(ACTIONS_FILE, 'w') as f:
                json.dump(default_actions, f, indent=4)
            return default_actions
        else:
            try:
                with open(ACTIONS_FILE, 'r') as f:
                    actions = json.load(f)
            except Exception as e:
                print(f"Error al leer el archivo de configuración: {e}")
                actions = {}

            # Asegurarse de que Button 5 tenga la estructura correcta
            if isinstance(actions.get("Button 5"), str):
                actions["Button 5"] = {
                    "inverted": False,
                    "sensitivity": 100,
                    "function": "Scroll Horizontal"
                }
                self.save_actions(actions)

            # Asegurarse de que Button 1 tenga la estructura correcta
            btn1 = actions.get("Button 1")
            if isinstance(btn1, str):
                actions["Button 1"] = {
                    "action": btn1,
                    "gestures_enabled": False,
                    "gesture_up": "",
                    "gesture_down": "",
                    "gesture_left": "",
                    "gesture_right": ""
                }
            elif isinstance(btn1, dict):
                if "action" not in btn1:
                    btn1["action"] = ""
                if "gestures_enabled" not in btn1:
                    btn1["gestures_enabled"] = False
                if "gesture_up" not in btn1:
                    btn1["gesture_up"] = ""
                if "gesture_down" not in btn1:
                    btn1["gesture_down"] = ""
                if "gesture_left" not in btn1:
                    btn1["gesture_left"] = ""
                if "gesture_right" not in btn1:
                    btn1["gesture_right"] = ""
                actions["Button 1"] = btn1

            self.save_actions(actions)
            return actions

    def save_actions(self, actions=None):
        if actions is None:
            actions = self.actions
        try:
            with open(ACTIONS_FILE, 'w') as f:
                json.dump(actions, f, indent=4)
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")

    # Métodos para Botones (excepto Button 5)
    def get_action(self, button_name):
        if button_name == "Button 1":
            b1 = self.actions.get("Button 1", {})
            if isinstance(b1, dict):
                return b1.get("action", "")
            return b1
        elif button_name == "Button 5":
            return None
        else:
            return self.actions.get(button_name, "")

    def set_action(self, button_name, action):
        if button_name == "Button 1":
            b1 = self.actions.get("Button 1", {})
            if not isinstance(b1, dict):
                b1 = {
                    "action": "",
                    "gestures_enabled": False,
                    "gesture_up": "",
                    "gesture_down": "",
                    "gesture_left": "",
                    "gesture_right": ""
                }
            b1["action"] = action
            self.actions["Button 1"] = b1
            self.save_actions()
        elif button_name == "Button 5":
            pass
        else:
            self.actions[button_name] = action
            self.save_actions()

    # Métodos para Button 1 (Gestos)
    def get_gestures_enabled(self):
        b1 = self.actions.get("Button 1", {})
        if isinstance(b1, dict):
            return b1.get("gestures_enabled", False)
        return False

    def set_gestures_enabled(self, enabled: bool):
        b1 = self.actions.get("Button 1", {})
        if not isinstance(b1, dict):
            b1 = {
                "action": "",
                "gestures_enabled": enabled,
                "gesture_up": "",
                "gesture_down": "",
                "gesture_left": "",
                "gesture_right": ""
            }
        else:
            b1["gestures_enabled"] = enabled
        self.actions["Button 1"] = b1
        self.save_actions()

    def get_gesture_action(self, direction: str) -> str:
        b1 = self.actions.get("Button 1", {})
        if not isinstance(b1, dict):
            return ""
        return b1.get(f"gesture_{direction}", "")

    def set_gesture_action(self, direction: str, action_value: str):
        b1 = self.actions.get("Button 1", {})
        if not isinstance(b1, dict):
            b1 = {
                "action": "",
                "gestures_enabled": False,
                "gesture_up": "",
                "gesture_down": "",
                "gesture_left": "",
                "gesture_right": ""
            }
        b1[f"gesture_{direction}"] = action_value
        self.actions["Button 1"] = b1
        self.save_actions()

    # Métodos para Button 5
    def get_inversion(self):
        btn5 = self.actions.get("Button 5", {})
        if isinstance(btn5, dict):
            return btn5.get("inverted", False)
        else:
            self.actions["Button 5"] = {
                "inverted": False,
                "sensitivity": 100,
                "function": "Scroll Horizontal"
            }
            self.save_actions()
            return False

    def set_inversion(self, inverted: bool):
        btn5 = self.actions.get("Button 5", {})
        if not isinstance(btn5, dict):
            btn5 = {
                "inverted": inverted,
                "sensitivity": 100,
                "function": "Scroll Horizontal"
            }
        else:
            btn5["inverted"] = inverted
        self.actions["Button 5"] = btn5
        self.save_actions()

    def get_sensitivity(self):
        btn5 = self.actions.get("Button 5", {})
        if isinstance(btn5, dict):
            return btn5.get("sensitivity", 100)
        else:
            self.actions["Button 5"] = {
                "inverted": False,
                "sensitivity": 100,
                "function": "Scroll Horizontal"
            }
            self.save_actions()
            return 100

    def set_sensitivity(self, sensitivity: int):
        btn5 = self.actions.get("Button 5", {})
        if not isinstance(btn5, dict):
            btn5 = {
                "inverted": False,
                "sensitivity": sensitivity,
                "function": "Scroll Horizontal"
            }
        else:
            btn5["sensitivity"] = sensitivity
        self.actions["Button 5"] = btn5
        self.save_actions()

    def get_wheel_function(self):
        config_5 = self.actions.get("Button 5", {})
        return config_5.get("function", "Scroll Horizontal")

    def set_wheel_function(self, func):
        config_5 = self.actions.get("Button 5", {})
        config_5["function"] = func
        self.actions["Button 5"] = config_5
        self.save_actions()
