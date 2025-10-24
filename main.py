import cv2
import mediapipe as mp
import numpy as np
import mido
from pygrabber.dshow_graph import FilterGraph 

# Inicializar Mediapipe
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Configurar salida MIDI
midi_port = mido.open_output("loopMIDI Port 1 2")  # Asegúrate de que este nombre coincida con tu puerto loopMIDI
#En un futuro midi_port_teensy = mido.open_output ("Teensy MIDI")

# Función para enviar mensajes MIDI
def send_midi(cc, value):
    value = max(0, min(127, int(value)))  # Limitar el valor entre 0 y 127
    midi_msg = mido.Message('control_change', channel=0, control=cc, value=value)
    midi_port.send(midi_msg)
    #En un futuro midi_port_teensy.send(midi_msg)

# Función para mostrar las cámaras disponibles
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

# Abrir la cámara seleccionada
video = cv2.VideoCapture(selected_camera_index)

# Usar el contexto de Mediapipe Hands
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, image = video.read()
        if not ret:
            break

        # Invertir la imagen horizontalmente para que actúe como un espejo
        image = cv2.flip(image, 1)

        # Convertir la imagen a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Procesar la imagen para detectar manos
        hand_results = hands.process(image_rgb)

        midpoints = []
        hand_distances = []  # Guardar las distancias de las manos

        h, w, _ = image.shape  # Dimensiones de la imagen

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]

                thumb_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                index_point = (int(index_tip.x * w), int(index_tip.y * h))

                # Dibujar línea entre el pulgar y el índice
                cv2.line(image, thumb_point, index_point, (0, 255, 0), 2)

                midpoint = ((thumb_point[0] + index_point[0]) // 2,
                            (thumb_point[1] + index_point[1]) // 2)
                midpoints.append(midpoint)

                distance = np.linalg.norm(np.array(thumb_point) - np.array(index_point))
                hand_distances.append(distance)

                # Dibujar puntos rojos en los extremos (pulgar e índice)
                cv2.circle(image, thumb_point, 5, (0, 0, 255), -1)
                cv2.circle(image, index_point, 5, (0, 0, 255), -1)

        center_point = None
        midpoint_distance = 0
        if len(midpoints) == 2:
            # Dibujar línea entre puntos medios
            cv2.line(image, midpoints[0], midpoints[1], (255, 255, 0), 2)

            center_point = ((midpoints[0][0] + midpoints[1][0]) // 2,
                            (midpoints[0][1] + midpoints[1][1]) // 2)

            cv2.circle(image, center_point, 5, (255, 255, 255), -1)  # Cambiado a blanco

            midpoint_distance = np.linalg.norm(np.array(midpoints[0]) - np.array(midpoints[1])) / 2  # Mitad de la distancia

        # Dibujar barras de volumen
        bar_width = 30
        colors = [(0, 255, 0), (0, 255, 0), (255, 255, 0)]  # Verde, verde, azul
        for i, dist in enumerate(hand_distances + [midpoint_distance if center_point else 0]):
            color = colors[i % len(colors)]
            max_height = h - 20
            bar_height = int((dist / w) * max_height)

            # Dibujar la barra
            cv2.rectangle(image, (10 + i * bar_width, h - bar_height),
                          (10 + (i + 1) * bar_width - 5, h - 10), color, -1)

        if center_point:
            # Calcular las distancias desde el centro de la imagen
            dist_x = center_point[0] - w // 2
            dist_y = h // 2 - center_point[1]

            # Escalar los valores entre 0 y 127
            scaled_dist_x = int((dist_x + (w // 2)) / w * 127)
            scaled_dist_y = int((dist_y + (h // 2)) / h * 127)

            # Dibujar la barra horizontal en la parte superior (cambiado a blanco)
            horizontal_length = int((dist_x / (w // 2)) * (w // 2))
            cv2.rectangle(image, (w // 2, 10),
                          (w // 2 + horizontal_length, 30),
                          (255, 255, 255), -1)

            send_midi(21, scaled_dist_x)  # Barra blanca (horizontal superior)

            # Dibujar la barra vertical en la parte derecha (color rojo)
            vertical_length = int((dist_y / (h // 2)) * (h // 2))
            cv2.rectangle(image, (w - 30, h // 2),
                          (w - 10, h // 2 - vertical_length),
                          (0, 0, 255), -1)

            send_midi(22, scaled_dist_y)  # Barra roja (vertical derecha)

        # Enviar valores MIDI para las otras barras
        send_midi(23, hand_distances[0] if len(hand_distances) > 0 else 0)  # Primera barra verde
        send_midi(24, hand_distances[1] if len(hand_distances) > 1 else 0)  # Segunda barra verde
        send_midi(25, midpoint_distance if center_point else 0)            # Barra azul basada en la mitad de la distancia

        # Mostrar la imagen
        cv2.imshow("Frame", image)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Liberar recursos
video.release()
cv2.destroyAllWindows()
