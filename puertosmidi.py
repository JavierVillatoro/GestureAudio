#PARA VER LOS PUERTOS MIDI DISPONIBLES , EN MI CASO LOOPMIDI PORT 1 2 

import mido

# Lista de puertos de salida MIDI
print("Puertos MIDI disponibles:")
for port in mido.get_output_names():
    print(port)
    
#CORREGIR NOMBRE DE DISTANCIAS 

#Primer valor (distancia entre el pulgar y el índice de la primera mano): CC 21
#Segundo valor (distancia entre el pulgar y el índice de la segunda mano, si existe): CC 22
#Tercer valor (distancia entre los puntos medios de ambas manos, si ambas manos están detectadas): CC 23
#Cuarto valor (distancia horizontal del punto central entre las manos con respecto al centro de la imagen): CC 24
#Quinto valor (distancia vertical del punto central entre las manos con respecto al centro de la imagen): CC 25