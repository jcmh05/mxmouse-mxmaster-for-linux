import subprocess
import threading
from evdev import InputDevice, categorize, ecodes, list_devices


class ActionExecutor:
    def execute(self, action):
        if isinstance(action, dict):
            return
        elif action.startswith("Command:"):
            command = action.split("Command:")[1].strip()
            subprocess.Popen(command, shell=True)
        else:
            predefined_actions = {
                "Copy":          "xdotool key ctrl+c",
                "Paste":         "xdotool key ctrl+v",
                "Volume Up":     "xdotool key XF86AudioRaiseVolume",
                "Volume Down":   "xdotool key XF86AudioLowerVolume",
                "Mute":          "xdotool key XF86AudioMute",
                "Undo":          "xdotool key ctrl+z",
                "Redo":          "xdotool key ctrl+shift+z",
                "Scroll Up":     "xdotool click 4",
                "Scroll Down":   "xdotool click 5",
                "Scroll Left":   "xdotool click 6",
                "Scroll Right":  "xdotool click 7",
                "Left Click":    "xdotool click 1",
                "Right Click":   "xdotool click 3",
                "Forward":       "xdotool key XF86Forward",
                "Back":          "xdotool key XF86Back",
                "Open Terminal": "gnome-terminal",
                "Show Desktop":  "xdotool key super+d",
                "Close Window":  "xdotool key ctrl+w",
            }
            cmd = predefined_actions.get(action)
            if cmd:
                subprocess.Popen(cmd, shell=True)
            else:
                print(f"Acción predefinida desconocida: {action}")


class MouseEventListener(threading.Thread):
    BUTTON_XINPUT_MAP = {
        "Button 1": 1,
        "Button 2": 8,
        "Button 3": 9,
        "Button 4": 4,
        "Button 5": 5,
        "ScrollLeft": 6,
        "ScrollRight": 7,
    }

    def __init__(self, config_manager, action_executor):
        super().__init__()
        self.config_manager = config_manager
        self.action_executor = action_executor
        self.running = True

        self.device = self.find_mouse_device()
        self.xinput_id = self.find_xinput_id("MX Master 3S")  # Ajusta el nombre exacto
        if self.xinput_id is None:
            print("WARNING: No se pudo encontrar el ID de XInput para MX Master 3S. El bloqueo del cursor no funcionará.")
        self.master_pointer_id = self.find_master_pointer_id()

        self.button1_pressed = False
        self.button1_gesture_detected = False
        self.button1_movement = {'x': 0, 'y': 0}
        self.gesture_threshold = 50
        self.cursor_position = (0, 0)

        self.original_button_map = self.get_xinput_button_map()
        if self.xinput_id and self.original_button_map:
            self.adjust_xinput_mappings()

    def find_mouse_device(self):
        for device in [InputDevice(path) for path in list_devices()]:
            if 'MX Master' in device.name:
                print(f"Dispositivo evdev encontrado: {device.path} - {device.name}")
                return device
        raise Exception("Ratón Logitech MX Master 3S no encontrado en evdev.")

    def find_xinput_id(self, name_hint):
        try:
            result = subprocess.check_output(["xinput", "list"], universal_newlines=True)
            for line in result.splitlines():
                if name_hint in line:
                    parts = line.split()
                    for p in parts:
                        if p.startswith("id="):
                            return int(p.split("=")[1])
            return None
        except Exception as e:
            print(f"No se pudo ejecutar xinput list: {e}")
            return None

    def find_master_pointer_id(self):
        try:
            result = subprocess.check_output(["xinput", "list", "--short"], universal_newlines=True)
            for line in result.splitlines():
                if "Virtual core pointer" in line:
                    parts = line.split()
                    for p in parts:
                        if p.startswith("id="):
                            return int(p.split("=")[1])
            return 2
        except Exception as e:
            print(f"No se pudo obtener master pointer id: {e}")
            return 2

    def get_cursor_position(self):
        try:
            result = subprocess.check_output(["xdotool", "getmouselocation"], universal_newlines=True)
            parts = result.split()
            x = int(parts[0].split(':')[1])
            y = int(parts[1].split(':')[1])
            return x, y
        except Exception as e:
            print(f"Error al obtener posición del cursor: {e}")
            return None, None

    def set_cursor_position(self, x, y):
        try:
            subprocess.check_call(["xdotool", "mousemove", str(x), str(y)])
            print(f"Cursor movido a ({x}, {y})")
        except Exception as e:
            print(f"Error al establecer posición del cursor: {e}")

    def get_xinput_button_map(self):
        try:
            result = subprocess.check_output(["xinput", "get-button-map", str(self.xinput_id)], universal_newlines=True)
            return list(map(int, result.strip().split()))
        except Exception as e:
            print(f"Error al obtener mapeo de botones de xinput: {e}")
            return []

    def set_xinput_button_map(self, new_map):
        try:
            subprocess.check_call(["xinput", "set-button-map", str(self.xinput_id)] + list(map(str, new_map)))
            print("[Cursor] Mapeo de botones actualizado.")
        except Exception as e:
            print(f"Error al establecer mapeo de botones de xinput: {e}")

    def adjust_xinput_mappings(self):
        new_map = self.original_button_map.copy()

        # Desactivar botones 2 y 3 si tienen acciones personalizadas
        for button_name in ["Button 2", "Button 3"]:
            action = self.config_manager.get_action(button_name)
            if action and action not in ["Back", "Forward"]:
                xinput_button = self.BUTTON_XINPUT_MAP.get(button_name)
                if xinput_button and xinput_button <= len(new_map):
                    new_map[xinput_button - 1] = 0  # Desactivar botón
                    print(f"[XInput] {button_name} desactivado para acción personalizada.")

        # Desactivar scroll horizontal si tiene acción personalizada
        wheel_function = self.config_manager.get_wheel_function()
        if wheel_function != "Scroll Horizontal":
            for scroll_dir in ["ScrollLeft", "ScrollRight"]:
                xinput_button = self.BUTTON_XINPUT_MAP.get(scroll_dir)
                if xinput_button and xinput_button <= len(new_map):
                    new_map[xinput_button - 1] = 0  # Desactivar botón de scroll
                    print(f"[XInput] {scroll_dir} desactivado para acción personalizada.")

        self.set_xinput_button_map(new_map)

    def run(self):
        for event in self.device.read_loop():
            if not self.running:
                break

            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                button = self.map_code_to_button(key_event.scancode)
                if button == "Button 1":
                    if key_event.keystate == key_event.key_down:
                        self.handle_button1_press()
                    elif key_event.keystate == key_event.key_up:
                        self.handle_button1_release()
                elif button and button != "Button 5":
                    if key_event.keystate == key_event.key_down:
                        action = self.config_manager.get_action(button)
                        if action:
                            self.action_executor.execute(action)
            elif event.type == ecodes.EV_REL:
                if event.code == ecodes.REL_HWHEEL:
                    self.handle_hwheel(event.value)
                elif event.code == ecodes.REL_HWHEEL_HI_RES:
                    self.handle_hwheel_hi_res(event.value)
                elif event.code in [ecodes.REL_X, ecodes.REL_Y]:
                    self.handle_mouse_move(event)

    def map_code_to_button(self, scancode):
        scancode_mapping = {
            277: "Button 1",
            276: "Button 2",
            275: "Button 3",
            274: "Button 4",
            12:  "Button 5",
        }
        return scancode_mapping.get(scancode, None)

    def handle_button1_press(self):
        if not self.button1_pressed:
            self.button1_pressed = True
            self.button1_gesture_detected = False
            self.button1_movement = {'x': 0, 'y': 0}
            self.cursor_position = self.get_cursor_position() or (0, 0)
            print("[Button 1] Pulsado. Cursor guardado en:", self.cursor_position)
            self.float_device()

    def handle_button1_release(self):
        if self.button1_pressed:
            self.button1_pressed = False
            if not self.button1_gesture_detected:
                action = self.config_manager.get_action("Button 1")
                if action:
                    self.action_executor.execute(action)
                    print("[Button 1] Acción de pulsación simple ejecutada")
            else:
                print("[Button 1] Gesto detectado, no se ejecuta pulsación simple.")
            self.reattach_device()
            self.set_cursor_position(*self.cursor_position)

    def handle_mouse_move(self, event):
        if self.button1_pressed and not self.button1_gesture_detected:
            if event.code == ecodes.REL_X:
                self.button1_movement['x'] += event.value
            elif event.code == ecodes.REL_Y:
                self.button1_movement['y'] += event.value

            abs_x = abs(self.button1_movement['x'])
            abs_y = abs(self.button1_movement['y'])

            if abs_x > self.gesture_threshold or abs_y > self.gesture_threshold:
                if abs_x > abs_y:
                    direction = "right" if self.button1_movement['x'] > 0 else "left"
                else:
                    direction = "down" if self.button1_movement['y'] > 0 else "up"

                gesture_action = self.config_manager.get_gesture_action(direction)
                if gesture_action:
                    self.action_executor.execute(gesture_action)
                    print(f"[Button 1] Gesto detectado: {direction} -> {gesture_action}")
                else:
                    print(f"[Button 1] Gesto detectado: {direction}, pero sin acción asignada.")
                self.button1_gesture_detected = True

    def handle_hwheel(self, value):
        wheel_function = self.config_manager.get_wheel_function()
        inverted = self.config_manager.get_inversion()
        sensitivity = self.config_manager.get_sensitivity()

        direction = -value if inverted else value
        clicks = max(abs(int((sensitivity / 100) * direction)), 1)

        if wheel_function == "Scroll Horizontal":
            self.scroll_horizontal(direction, clicks, sensitivity)
        elif wheel_function == "Volume Control":
            self.volume_control(direction, clicks, sensitivity)
        elif wheel_function == "Zoom":
            self.zoom(direction, clicks, sensitivity)
        else:
            self.scroll_horizontal(direction, clicks, sensitivity)

    def handle_hwheel_hi_res(self, value):
        normalized = value // 120
        self.handle_hwheel(normalized)

    def scroll_horizontal(self, direction, clicks, sensitivity):
        if direction > 0:
            for _ in range(clicks):
                subprocess.Popen(["xdotool", "click", "7"])
            print(f"[Scroll Horizontal] DERECHA => clicks={clicks} sens={sensitivity}")
        elif direction < 0:
            for _ in range(clicks):
                subprocess.Popen(["xdotool", "click", "6"])
            print(f"[Scroll Horizontal] IZQUIERDA => clicks={clicks} sens={sensitivity}")

    def volume_control(self, direction, clicks, sensitivity):
        key = "XF86AudioRaiseVolume" if direction > 0 else "XF86AudioLowerVolume"
        for _ in range(clicks):
            subprocess.Popen(["xdotool", "key", key])
        action = "Subir" if direction > 0 else "Bajar"
        print(f"[Volume Control] {action} => clicks={clicks} sens={sensitivity}")

    def zoom(self, direction, clicks, sensitivity):
        key = "ctrl+KP_Add" if direction > 0 else "ctrl+KP_Subtract"
        for _ in range(clicks):
            subprocess.Popen(["xdotool", "key", key])
        action = "Acercar" if direction > 0 else "Alejar"
        print(f"[Zoom] {action} => clicks={clicks} sens={sensitivity}")

    def float_device(self):
        if self.xinput_id:
            try:
                subprocess.check_call(["xinput", "float", str(self.xinput_id)])
                print(f"[Cursor] Dispositivo {self.xinput_id} desconectado (float).")
            except subprocess.CalledProcessError as e:
                print(f"Error al hacer float en xinput: {e}")

    def reattach_device(self):
        if self.xinput_id:
            try:
                subprocess.check_call(["xinput", "reattach", str(self.xinput_id), str(self.master_pointer_id)])
                print(f"[Cursor] Dispositivo {self.xinput_id} reenganchado a maestro {self.master_pointer_id}.")
            except subprocess.CalledProcessError as e:
                print(f"Error al hacer reattach en xinput: {e}")

    def stop(self):
        self.running = False
        self.reattach_device()
        print("[MouseEventListener] Detenido.")
