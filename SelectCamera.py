import cv2
from pygrabber.dshow_graph import FilterGraph 

def select_camera():
    # Usar FilterGraph para obtener los nombres de las cámaras
    graph = FilterGraph()
    device_names = graph.get_input_devices()  # Obtener nombres de las cámaras
    
    if not device_names:
        print("No se encontraron cámaras disponibles.")
        return None

    print("Cámaras disponibles:")
    for i, cam_name in enumerate(device_names):
        print(f"{i + 1}. {cam_name}")

    choice = -1
    while choice < 1 or choice > len(device_names):
        try:
            choice = int(input(f"Seleccione una cámara (1-{len(device_names)}): "))
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número.")
    
    return choice - 1  # Devolver el índice de la cámara seleccionada

# Seleccionar la cámara
selected_camera_index = select_camera()

if selected_camera_index is None:
    print("No se puede iniciar el programa sin cámara.")
    exit()
