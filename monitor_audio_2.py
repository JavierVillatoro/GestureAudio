#Mejorar pantalla visual , no funciona 

#Asignar estos a comandos o algo , que lea Controlador primario... , y solo muestre ese junto a los deas, por ejemplo. 
# Ahora muestra todas las entradas salidas.
#Entrada PC ---------------8   Controlador primario de captura de sonido (input) 
#Salida Headphones PC------13  Headphone (Realtek(R) Audio) (output)
#HACER LO MISMO CON TARJETA   

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ==== CONFIGURACIÓN ====
BUFFER = 1024          # tamaño de bloque de audio
DURATION = 5           # duración visible del loop (segundos)
FS = 44100             # frecuencia de muestreo (Hz)

def listar_dispositivos():
    print("\n=== Dispositivos de audio disponibles ===")
    dispositivos = sd.query_devices()
    for i, d in enumerate(dispositivos):
        tipo = []
        if d['max_input_channels'] > 0:
            tipo.append("input")
        if d['max_output_channels'] > 0:
            tipo.append("output")
        print(f"{i}: {d['name']} ({', '.join(tipo)})")
    print("=========================================\n")

def seleccionar_dispositivo(tipo):
    while True:
        try:
            idx = int(input(f"Selecciona el dispositivo de {tipo} (número): "))
            info = sd.query_devices(idx)
            if (tipo == "entrada" and info['max_input_channels'] > 0) or \
               (tipo == "salida" and info['max_output_channels'] > 0):
                return idx
            else:
                print("⚠️  Ese dispositivo no tiene canales de " + tipo)
        except Exception as e:
            print("Error:", e)

# === Selección de dispositivos ===
listar_dispositivos()
input_dev = seleccionar_dispositivo("entrada")
output_dev = seleccionar_dispositivo("salida")

# === Inicializar buffer circular ===
n_samples = int(DURATION * FS)
buffer = np.zeros(n_samples)

# === Configurar gráfica ===
fig, ax = plt.subplots()
line, = ax.plot(buffer)
ax.set_ylim([-1, 1])
ax.set_xlim([0, n_samples])
ax.set_title("Señal de audio en vivo")
ax.set_xlabel("Muestras")
ax.set_ylabel("Amplitud")

# === Callback de audio ===
def callback(indata, outdata, frames, time, status):
    global buffer
    if status:
        print(status)
    # Copiar entrada -> salida (monitorización)
    outdata[:] = indata
    # Actualizar buffer circular
    buffer[:-frames] = buffer[frames:]
    buffer[-frames:] = indata[:, 0]

# === Iniciar stream ===
stream = sd.Stream(device=(input_dev, output_dev),
                   samplerate=FS,
                   blocksize=BUFFER,
                   channels=1,
                   callback=callback)

# === Función de actualización de la gráfica ===
def update_plot(frame):
    line.set_ydata(buffer)
    return line,

ani = animation.FuncAnimation(fig, update_plot, interval=30, blit=True)

print("\n🎤 Grabando y reproduciendo en tiempo real...")
print("Cierra la ventana para detener.\n")

with stream:
    plt.show()
