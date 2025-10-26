import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pedalboard import Pedalboard, Compressor, Gain, Reverb

# ==== CONFIGURACIÓN ====
BUFFER = 2048      # mayor estabilidad
DURATION = 5
FS = 44100

# ==== CADENA DE EFECTOS (más ligera) ====
board = Pedalboard([
    Compressor(threshold_db=-25, ratio=2.5),
    Gain(gain_db=0),  # sin ganancia adicional
    Reverb(room_size=1, damping=0.7, wet_level=0.9, dry_level=1)
])

# ==== SELECCIÓN DE DISPOSITIVOS ====
def listar_dispositivos():
    dispositivos = sd.query_devices()
    for i, d in enumerate(dispositivos):
        tipo = []
        if d['max_input_channels'] > 0:
            tipo.append("input")
        if d['max_output_channels'] > 0:
            tipo.append("output")
        print(f"{i}: {d['name']} ({', '.join(tipo)})")

listar_dispositivos()
input_dev = int(input("Selecciona dispositivo de entrada: "))
output_dev = int(input("Selecciona dispositivo de salida: "))

# ==== BUFFER Y GRÁFICA ====
n_samples = int(DURATION * FS)
buffer = np.zeros(n_samples)
fig, ax = plt.subplots()
line, = ax.plot(buffer)
ax.set_ylim([-1, 1])
ax.set_xlim([0, n_samples])
ax.set_title("Audio en vivo con reverb optimizada")

# ==== CALLBACK ====
def callback(indata, outdata, frames, time, status):
    global buffer
    if status:
        print(status)
# Asegurar que haya 2 canales
    if indata.shape[1] == 1:
        audio_in = np.repeat(indata, 2, axis=1)  # duplicar mono a estéreo
    else:
        audio_in = indata

    processed = board(audio_in.T, FS)
    outdata[:] = processed.T

    # Actualizar buffer
    buffer[:-frames] = buffer[frames:]
    buffer[-frames:] = processed[0, :]

# ==== STREAM ====
stream = sd.Stream(device=(input_dev, output_dev),
                   samplerate=FS,
                   blocksize=BUFFER,
                   channels=2,
                   dtype='float32',
                   callback=callback)

def update_plot(frame):
    line.set_ydata(buffer)
    return line,

ani = animation.FuncAnimation(fig, update_plot, interval=30, blit=True)

print("\n🎛️ Procesando audio en tiempo real con reverb ligera...")
print("Cierra la ventana para detener.\n")

with stream:
    plt.show()



