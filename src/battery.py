# src/battery.py

import subprocess
import re

class BatteryManager:
    def __init__(self):
        # Intentaremos encontrar la ruta del dispositivo del mouse en upower
        self.device_path = self.find_mouse_device_path()

    def find_mouse_device_path(self):
        """
        Busca en la salida de 'upower -e' alguna ruta que contenga 'mouse' o 'hid' 
        y la devuelve. Ajusta los filtros si tu ratón aparece con otro nombre.
        """
        try:
            devices_output = subprocess.check_output(["upower", "-e"], universal_newlines=True)
            devices = devices_output.splitlines()
            for dev in devices:
                # Filtra por 'mouse' o 'hid_' en la ruta, depende de cómo aparezca en tu sistema
                if "mouse" in dev.lower() or "hid" in dev.lower():
                    return dev.strip()  # Por ejemplo: /org/freedesktop/UPower/devices/mouse_hid_...
        except Exception as e:
            print(f"Error buscando dispositivo en upower: {e}")

        # Si no lo encuentra, podrías devolver None
        return None

    def get_battery_percentage(self):
        """
        Obtiene el porcentaje de la batería del dispositivo que encontramos en find_mouse_device_path().
        Si no encuentra el dispositivo, devuelve 0.
        """
        if not self.device_path:
            # Si no pudo detectar el ratón mediante upower
            return 0

        try:
            info = subprocess.check_output(["upower", "-i", self.device_path], universal_newlines=True)
            # Buscar línea con 'percentage:'
            match = re.search(r'percentage:\s+(\d+)%', info)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"Error al leer porcentaje de batería con upower: {e}")

        return 0
