import numpy as np
import matplotlib.pyplot as plt

# Parámetros para este ejercicio
Pe_ejercicio = 0.2  # Probabilidad de error de trama para este ejercicio (20%)
a_valores_ejercicio = np.linspace(0.01, 10, 500)

# Configuraciones de las Curvas para el Ejercicio
# Curva A: Protocolo X con Ventana N=2
N_A_ejercicio = 1 # Stop-and-Wait siempre tiene N=1
# Curva B: Protocolo Y con Ventana N=7
N_B_ejercicio = 7
# Curva C: Protocolo Z con Ventana N=4
N_C_ejercicio = 4

# --- CÁLCULOS DE EFICIENCIA PARA EL EJERCICIO ---

# 1. Curva A (Azul): Asumimos que es Parada y Espera (N=1)
eta_A_ejercicio = (1 - Pe_ejercicio) / (1 + 2 * a_valores_ejercicio)

# 2. Curva B (Verde): Asumimos que es Adelante Atrás N (N=7)
U_max_B_ejercicio = (1 - Pe_ejercicio) / (1 - Pe_ejercicio + N_B_ejercicio * Pe_ejercicio) # 0.8 / (0.8 + 7*0.2) = 0.8 / (0.8 + 1.4) = 0.8 / 2.2 = 0.3636
U_window_limit_B_ejercicio = N_B_ejercicio / (1 + 2 * a_valores_ejercicio)
eta_B_ejercicio = np.minimum(1, U_window_limit_B_ejercicio) * U_max_B_ejercicio

# 3. Curva C (Roja): Asumimos que es Repetición Selectiva (N=4)
U_max_C_ejercicio = 1 - Pe_ejercicio # 0.8
U_window_limit_C_ejercicio = N_C_ejercicio / (1 + 2 * a_valores_ejercicio)
eta_C_ejercicio = np.minimum(1, U_window_limit_C_ejercicio) * U_max_C_ejercicio


# Crear la gráfica para el ejercicio
plt.figure(figsize=(10, 6))

plt.plot(a_valores_ejercicio, eta_A_ejercicio, label='Curva A', color='blue', linewidth=2)
plt.plot(a_valores_ejercicio, eta_B_ejercicio, label='Curva B', color='green', linewidth=2)
plt.plot(a_valores_ejercicio, eta_C_ejercicio, label='Curva C', color='red', linewidth=2)

# Añadir títulos y etiquetas
plt.title('Gráfica de Análisis ARQ (Ejercicio)', fontsize=14)
plt.xlabel('$a$ (Retardo de Propagación en Tiempos de Trama)', fontsize=12)
plt.ylabel('Eficiencia ($\eta$)', fontsize=12)

# Añadir una cuadrícula para mejor lectura
plt.grid(True, linestyle='--', alpha=0.6)

# Añadir la leyenda
plt.legend(loc='upper right', fontsize=10)

# Limitar el eje y a 1.05
plt.ylim(0, 1.05)
plt.xlim(0, 10)

# Guardar la gráfica
plt.savefig('grafica_ejercicio_arq.png')

print("Se ha generado la gráfica 'grafica_ejercicio_arq.png'")