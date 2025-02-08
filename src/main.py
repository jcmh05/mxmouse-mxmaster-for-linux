import sys
import os
import time
import threading
from PyQt5.QtWidgets import QApplication
from src.gui import MainWindow
from src.config_manager import ConfigManager
from src.backend import MouseEventListener, ActionExecutor
from src.battery import BatteryManager

def main():
    # Inicializar la configuración y el ejecutor de acciones
    config_manager = ConfigManager()
    action_executor = ActionExecutor()

    app = QApplication(sys.argv)
    window = MainWindow(config_manager)
    
    # Si se pasa el parámetro "--hidden", no mostramos la ventana (o la ocultamos)
    auto_hidden = "--hidden" in sys.argv
    if auto_hidden:
        window.hide()  # Inicia minimizada (en la bandeja)
        time.sleep(5)
    else:
        window.show()

    # Inicializar el listener de eventos
    try:
        event_listener = MouseEventListener(config_manager, action_executor)
        event_listener.start()
    except Exception as e:
        print(f"Error al iniciar el listener de eventos: {e}")

    # Inicializar el gestor de batería en un hilo separado
    battery_manager = BatteryManager()

    def battery_updater():
        while True:
            percentage = battery_manager.get_battery_percentage()
            window.comm.update_battery.emit(percentage)
            time.sleep(60)

    battery_thread = threading.Thread(target=battery_updater, daemon=True)
    battery_thread.start()

    exit_code = app.exec_()

    # Detener el listener de eventos al cerrar la aplicación
    event_listener.stop()
    event_listener.join()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
