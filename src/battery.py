import subprocess
import re

class BatteryManager:
    def __init__(self):
        self.device_path = None
        # Verificar si upower está disponible
        try:
            subprocess.check_output(["which", "upower"], universal_newlines=True)
            self.device_path = self.find_mouse_device_path()
            if not self.device_path:
                print("Dispositivo de ratón no encontrado con upower.")
        except Exception as e:
            print("Upower no está disponible o error al verificar:", e)
    
    def find_mouse_device_path(self):
        try:
            devices_output = subprocess.check_output(["upower", "-e"], universal_newlines=True)
            devices = devices_output.splitlines()
            for dev in devices:
                if "mouse" in dev.lower() or "hid" in dev.lower():
                    return dev.strip()  # Ej: /org/freedesktop/UPower/devices/mouse_hid_...
        except Exception as e:
            print("Error buscando dispositivo en upower:", e)
        return None

    def get_battery_percentage(self):
        if not self.device_path:
            return 0  # O podrías retornar None, según tu lógica
        try:
            info = subprocess.check_output(["upower", "-i", self.device_path], universal_newlines=True)
            match = re.search(r'percentage:\s+(\d+)%', info)
            if match:
                return int(match.group(1))
        except Exception as e:
            print("Error al leer porcentaje de batería con upower:", e)
        return 0