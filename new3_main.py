import cv2
import mediapipe as mp
import numpy as np
import mido
from pygrabber.dshow_graph import FilterGraph 
import time

# Inicializar Mediapipe
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Configurar salida MIDI
midi_port = mido.open_output("loopMIDI Port 1 2")  # Asegúrate de que este nombre coincida con tu puerto loopMIDI

# Función para enviar mensajes MIDI
def send_midi(cc, value):
    value = max(0, min(127, int(value)))  # Limitar el valor entre 0 y 127
    midi_msg = mido.Message('control_change', channel=0, control=cc, value=value)
    midi_port.send(midi_msg)

# Función para mostrar las cámaras disponibles
def select_camera():
    graph = FilterGraph()
    device_names = graph.get_input_devices()

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

    return choice - 1

# Seleccionar la cámara
selected_camera_index = select_camera()

if selected_camera_index is None:
    print("No se puede iniciar el programa sin cámara.")
    exit()

# Abrir la cámara seleccionada
video = cv2.VideoCapture(selected_camera_index)

# Variables de activación
def is_center_active(center_point, w, h, cx, cy):
    center_tolerance = 20  # Tolerancia de proximidad al centro
    return abs(center_point[0] - cx) < center_tolerance and abs(center_point[1] - cy) < center_tolerance

activation_start_time = None
active = False
activation_duration = 2  # Tiempo necesario en segundos para activar/desactivar

# Usar el contexto de Mediapipe Hands
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, image = video.read()
        if not ret:
            break

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(image_rgb)

        h, w, _ = image.shape
        center_point = None
        midpoints = []
        hand_distances = []
        midpoint_distance = 0

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]

                thumb_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                index_point = (int(index_tip.x * w), int(index_tip.y * h))

                cv2.line(image, thumb_point, index_point, (0, 255, 0), 2)
                cv2.circle(image, thumb_point, 5, (0, 0, 255), -1)
                cv2.circle(image, index_point, 5, (0, 0, 255), -1)

                midpoint = ((thumb_point[0] + index_point[0]) // 2,
                            (thumb_point[1] + index_point[1]) // 2)
                midpoints.append(midpoint)

                distance = np.linalg.norm(np.array(thumb_point) - np.array(index_point))
                hand_distances.append(distance)

        if len(midpoints) == 2:
            cv2.line(image, midpoints[0], midpoints[1], (255, 255, 0), 2)
            center_point = ((midpoints[0][0] + midpoints[1][0]) // 2,
                            (midpoints[0][1] + midpoints[1][1]) // 2)
            cv2.circle(image, center_point, 5, (255, 255, 255), -1)
            midpoint_distance = np.linalg.norm(np.array(midpoints[0]) - np.array(midpoints[1])) / 2

        # Coordenadas de los círculos de activación
        main_circle_x, main_circle_y = w // 2, h // 2
        secondary_circle_x, secondary_circle_y = w // 2, h - (h // 10 * 2)

        # Verificar si el punto blanco está en alguno de los círculos
        if center_point and (is_center_active(center_point, w, h, main_circle_x, main_circle_y) or
                             is_center_active(center_point, w, h, secondary_circle_x, secondary_circle_y)):
            if activation_start_time is None:
                activation_start_time = time.time()
            elif time.time() - activation_start_time > activation_duration:
                active = not active
                activation_start_time = None
        else:
            activation_start_time = None

        # Dibujar los indicadores del centro
        main_center_color = (0, 0, 255) if active else (0, 0, 0)
        secondary_center_color = (0, 0, 255) if active else (0, 0, 0)
        
        cv2.circle(image, (main_circle_x, main_circle_y), 10, main_center_color, -1 if active else 1)
        cv2.circle(image, (secondary_circle_x, secondary_circle_y), 10, secondary_center_color, -1 if active else 1)
        
        # Mostrar barras y enviar MIDI solo si está activo
        if active:
            bar_width = 30
            colors = [(0, 255, 0), (0, 255, 0), (255, 255, 0)]
            for i, dist in enumerate(hand_distances + [midpoint_distance]):
                color = colors[i % len(colors)]
                max_height = h - 20
                bar_height = int((dist / w) * max_height)

                cv2.rectangle(image, (10 + i * bar_width, h - bar_height),
                              (10 + (i + 1) * bar_width - 5, h - 10), color, -1)

            if center_point:
                dist_x = center_point[0] - w // 2
                dist_y = h // 2 - center_point[1]

                scaled_dist_x = int((dist_x + (w // 2)) / w * 127)
                scaled_dist_y = int((dist_y + (h // 2)) / h * 127)

                horizontal_length = int((dist_x / (w // 2)) * (w // 2))
                cv2.rectangle(image, (w // 2, 10),
                              (w // 2 + horizontal_length, 30),
                              (255, 255, 255), -1)
                send_midi(21, scaled_dist_x)

                vertical_length = int((dist_y / (h // 2)) * (h // 2))
                cv2.rectangle(image, (w - 30, h // 2),
                              (w - 10, h // 2 - vertical_length),
                              (0, 0, 255), -1)
                send_midi(22, scaled_dist_y)

            send_midi(23, hand_distances[0] if len(hand_distances) > 0 else 0)
            send_midi(24, hand_distances[1] if len(hand_distances) > 1 else 0)
            send_midi(25, midpoint_distance if center_point else 0)

        cv2.imshow("Frame", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

video.release()
cv2.destroyAllWindows()
