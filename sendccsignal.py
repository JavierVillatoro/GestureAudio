import mido
import threading
import time

# Abrir puertos MIDI
port1 = mido.open_output("loopMIDI Port 1 2")

#CORREGIR NOMBRE DE DISTANCIAS 
# Lista de CC que se enviarán con sus descripciones
cc_controls = [
    (21, "horizontal----panning"),
    (22, "vertical----amplitud"),
    (23, "pulgar indice 1"),
    (24, "pulgar indice 2"),
    (25, "entre manos---filtro")
]

cc_value = 64  # Valor inicial para enviar en el mensaje CC
running = True  # Bandera para el envío constante del MIDI

def send_midi_continuously(cc):
    """Envía mensajes MIDI CC de forma continua mientras se espera confirmación del usuario."""
    global running
    toggle = True  # Alternar valor para simular movimiento
    while running:
        value = cc_value if toggle else cc_value + 1  # Alterna entre 64 y 65
        message = mido.Message('control_change', control=cc, value=value)
        port1.send(message)
        toggle = not toggle
        time.sleep(0.1)  # Enviar mensaje cada 100 ms

# Función principal
print("Mueve los parámetros que quieres mapear. Escribe 'ok' para continuar al siguiente parámetro.")

for cc, description in cc_controls:
    print(f"Enviando CC {cc}: {description}")
    running = True
    midi_thread = threading.Thread(target=send_midi_continuously, args=(cc,))
    midi_thread.start()

    # Esperar confirmación del usuario
    while input("Escribe 'ok' para continuar: ").strip().lower() != 'ok':
        print("Por favor, escribe 'ok' para continuar.")

    # Detener el envío continuo y esperar al hilo
    running = False
    midi_thread.join()

# Cerrar puertos MIDI
port1.close()

print("Programa finalizado.")
