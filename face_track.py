import tkinter

import cv2
import face_recognition as fr
import os
import numpy as np
from datetime import datetime
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk, ImageDraw, ImageFont

#Variables necesarias
fecha_hoy = datetime.today().strftime("%d-%m-%Y")
fotos_empleados = 'Empleados'
fotos_registro = os.path.join('Registros', fecha_hoy)
logs_registro = os.path.join('Control', fecha_hoy)
registro_hoy = os.path.join(logs_registro, "registro.csv")
mis_imagenes = []
nombres_empleados = []
camara_activa = False
empleados_registrados = set()

# Si no existe el directorio donde se guardan las fotos de los empleados, lo crea
if not os.path.exists(fotos_empleados):
    os.makedirs(fotos_empleados)

# Si no existe el directorio donde se guardan las fotos del registro de entrada, lo crea
if not os.path.exists(fotos_registro):
    os.makedirs(fotos_registro)

# Si no existe el directorio de registro del día, lo crea
if not os.path.exists(logs_registro):
    os.makedirs(logs_registro)

# Si no existe archivo de registro del día, lo crea
if not os.path.exists(registro_hoy):
    registro = open(registro_hoy, "w")
    registro.write(f"Nombre del empleado, Hora de entrada")
    registro.close()

# Crear base de datos
lista_empleados = os.listdir(fotos_empleados)

# Obtener imágenes y nombres de las imágenes
for nombre in lista_empleados:
    imagen_actual = cv2.imread(f'{fotos_empleados}\\{nombre}')
    mis_imagenes.append(imagen_actual)
    nombres_empleados.append(os.path.splitext(nombre)[0])


# Liberar recursos al cerrar la ventana
def on_closing():
    """
    Libera la cámara y destruye todas las ventanas al cerrar
    la aplicación
    """
    captura.release()
    cv2.destroyAllWindows()
    ventana.destroy()


# Codificar imágenes
def codificar(imagenes):
    """Codifica una lista de imagenes para que puedan ser
    leidas por el reconocimiento facial"""
    imagenes_codificadas = []
    for imagen in imagenes:
        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        codificado = fr.face_encodings(imagen)[0]
        imagenes_codificadas.append(codificado)
    return imagenes_codificadas


# Registrar el ingreso de un empleado
def registrar_ingresos(persona):
    """
    Registra el nombre del empleado y la hora en la que
    el reconocimiento facial detecta al empleado.
    Guarda los datos en el archivo 'registro.csv'
    :param persona: Nombre del empleado
    """
    if persona in empleados_registrados:
        return

    with open(registro_hoy, "a") as f:
            hora = datetime.now().strftime("%H:%M:%S")
            f.write(f"\n{persona}, {hora}")
            f.close()
            foto_registro(persona, hora)


# Tomar una foto del empleado
def foto_registro(persona, hora):
    """
    Guarda una foto del empleado en el momento en el que
    el reconocimiento facial detecta a un empleado.
    La foto se guarda con el formato 'nombreEmpleado_horaRegistro.jpg'
    :param persona: Nombre del empleado
    :param hora: Hora del registro
    """
    exito, fotograma = captura.read()
    if exito:
        hora = hora.replace(":", "-")
        ruta_guardado = f"{fotos_registro}\\{persona}_{hora}.jpg"
        cv2.imwrite(ruta_guardado, fotograma)
        print(f"Foto de {persona} guardada con éxito")

def texto_en_pantalla(texto):
    """
    Muestra un mensaje en el Label donse se muestra la grabación mientras detección facial
    está desactivada o en caso de que se detecte algún error.
    :param texto: Texto a mostrar en pantalla.
    """
    # Si la cámara está inactiva, mostrar un mensaje en texto blanco sobre fondo negro
    imagen = Image.new("RGB", (640, 480), (0, 0, 0))  # Crear una imagen en negro
    draw = ImageDraw.Draw(imagen)
    texto = texto
    fuente = ImageFont.truetype("verdana.ttf", size=28)

    # Redimensionar la ventana para que quepa la imagen completa y los botones
    ventana.geometry(f"{imagen.width}x{imagen.height + 50}")

    # Calcular el tamaño del texto usando textbbox
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    ancho_texto = bbox[2] - bbox[0]  # Ancho del texto
    alto_texto = bbox[3] - bbox[1]  # Alto del texto

    # Centrar el texto en la imagen
    posicion = ((640 - ancho_texto) // 2, (480 - alto_texto) // 2)
    # Dibujar el texto en la imagen
    draw.text(posicion, texto, font=fuente, fill=(255, 255, 255))  # Texto blanco

    # Convertir la imagen a un formato compatible con Tkinter
    imagen = ImageTk.PhotoImage(imagen)
    # Mostrar la imagen en el Label de la interfaz
    label_camara.config(image=imagen)
    label_camara.image = imagen


# Función para actualizar la cámara en la interfaz
def actualizar_camara():
    """
    Verifica si la cámara está activa.
    Si está activa, captura y procesa las imagenes.
    Si no está activa, muestra un mensaje en la interfaz
    Se repite cada 10 ms para mantener la actualización en tiempo real
    """
    global empleados_registrados  # Acceder a la variable global empleados_registrados

    # Solo actualizar si la cámara está activa
    if camara_activa:

        # Capturar un fotograma de la cámara
        exito, imagen = captura.read()

        # Si la captura fue exitosa
        if exito:
            # Reducir la resolución de la imagen para mejorar el rendimiento
            fx, fy = 0.25, 0.25  # Factores de escala para reducir la imagen
            imagen_pequena = cv2.resize(imagen, (0, 0), fx=fx, fy=fy)

            # Detectar caras en la imagen reducida
            cara_captura = fr.face_locations(imagen_pequena)

            # Si se detectaron caras
            if cara_captura:

                # Codificar las caras detectadas
                cara_codificada = fr.face_encodings(imagen_pequena, cara_captura)

                # Comparar cada cara detectada con las caras conocidas
                for caracodif, caraubic in zip(cara_codificada, cara_captura):

                    # Calcular la distancia entre la cara detectada y las caras conocidas
                    distancias = fr.face_distance(empleados_codificados, caracodif)

                    # Obtener el índice de la cara con la menor distancia (mejor coincidencia)
                    indice_coincidencia = np.argmin(distancias)

                    # Si la distancia es mayor a 0.6, considerar la cara como desconocida
                    if distancias[indice_coincidencia] > 0.6:
                        nombre = "Desconocido"
                        # Rojo para caras desconocidas
                        color = (0, 0, 255)
                    else:
                        # Obtener el nombre del empleado correspondiente a la cara detectada
                        nombre = nombres_empleados[indice_coincidencia]
                        # Verde para caras conocidas
                        color = (0, 255, 0)

                        # Registrar el ingreso si el empleado no ha sido registrado en esta sesión
                        if nombre != "Desconocido" and nombre not in empleados_registrados:
                            registrar_ingresos(nombre)
                            empleados_registrados.add(nombre)


                    # Ajustar las coordenadas de la cara a la resolución original
                    y1, x2, y2, x1 = caraubic
                    y1, y2, x1, x2 = int(y1 / fy), int(y2 / fy), int(x1 / fx), int(x2 / fx)

                    # Dibujar un rectángulo alrededor de la cara detectada
                    cv2.rectangle(imagen, (x1, y1), (x2, y2), color, 2)

                    # Dibujar un rectángulo relleno para el nombre
                    cv2.rectangle(imagen, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)

                    # Mostrar el nombre del empleado o "Desconocido" debajo del rectángulo
                    cv2.putText(imagen, nombre, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), 2)

            # Convertir la imagen de BGR (OpenCV) a RGB (PIL)
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

            # Convertir la imagen a un formato compatible con Tkinter
            imagen = Image.fromarray(imagen)
            imagen = ImageTk.PhotoImage(imagen)

            #Redimensionar la ventana para que quepa la imagen completa y los botones
            ventana.geometry(f"{imagen.width()}x{(imagen.height() + 50)}")

            # Mostrar la imagen en el Label de la interfaz
            label_camara.config(image=imagen)
            label_camara.image = imagen

        # Llamar a la función cada 10 ms para actualizar la cámara en tiempo real
        label_camara.after(10, actualizar_camara)

    else:
        texto_en_pantalla("Reconocimiento facial desactivado")


# Función para iniciar/detener la cámara
def toggle_camara():
    """
    Activa o desactiva la cámara
    """
    global camara_activa
    if camara_activa:
        boton_camara.config(text="Iniciar Cámara")
        camara_activa = False

    else:
        boton_camara.config(text="Detener Cámara")
        camara_activa = True
        actualizar_camara()


#Lista de imagenes de empleados ya codificadas
empleados_codificados = codificar(mis_imagenes)

# Crear la ventana principal
ventana = Tk()
ventana.title("FaceTrack")
ventana.geometry("640x480")
ventana.iconbitmap("icon.ico")

# Área para mostrar la cámara
label_camara = Label(ventana)
label_camara.pack()

# Texto que se muestra en pantalla al iniciar la aplicación
if len(lista_empleados) > 0 and camara_activa == False:
    texto_en_pantalla("Reconocimiento facial desactivado")

# Mensaje que indica que no hay fotos de empleados
if len(lista_empleados) == 0:
    texto_en_pantalla("No hay fotos de empleados")

#Frame donde se colocarán los botones
frame_botones = Frame(ventana)
frame_botones.pack(side="bottom", anchor="center", pady=10)

# Botón para iniciar/detener la cámara.
# Se muestra si hay fotos de empleados
if len(lista_empleados) > 0:
    boton_camara = Button(frame_botones, text="Iniciar Cámara", command=toggle_camara)
    boton_camara.pack(side="left", padx=25)

# Botón para salir de la aplicación
boton_salir = Button(frame_botones, text="Salir", command=on_closing)
boton_salir.pack(side="left")

# Inicializar la cámara
captura = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not captura.isOpened():
    print("No se pudo abrir la cámara")
    exit()

#Vincular la tecla 'q' a la funcion on_closing()
ventana.bind('q', lambda event: on_closing())

# Configurar la función on_closing para cuando se cierra la ventana
ventana.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar la ventana
ventana.mainloop()

