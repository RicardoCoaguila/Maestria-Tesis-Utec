#interfaz grafica Final
#18/07/2024

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

# Función para listar los puertos COM disponibles
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Función para iniciar la conexión serial
def start_serial_connection():
    try:
        global ser
        ser = serial.Serial(port=com_port.get(), baudrate=int(baud_rate.get()), timeout=1)
        messagebox.showinfo("Información", "Conexión serial iniciada")
        start_reading()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Función para leer datos del puerto serial
def read_serial_data():
    global running
    global peso_escalar
    global mensaje
    while running:
        try:
            line = ser.readline().decode('utf-8').strip()
            mensaje="Leendo Data"
            if line:
                data = line.split(',')
                print(data)
                if len(data) == 13:
                    estado.set(data[0])  # Actualiza el estado en la interfaz gráfica
                    SpPosicion.append(float(data[6]))#SP posición
                    velocidad.append(float(data[7]))#velocidad
                    Output1a.append(float(data[8]))#CV
                    posicion.append(float(data[9]))#posicion
                    if data[0] == "m4":
                        peso.append(float(data[10])) #peso
                        pesoset.append(float(data[11]))
                        peso_escalar = float(data[10])
                    if data[0] == "m10":
                        peso.append(float(data[10])) #peso
                        peso2.append(float(data[12])) #peso mojado
                    if len(SpPosicion) > 2000:#limite de puntos que lee del arduino.
                        SpPosicion.pop(0)
                        velocidad.pop(0)
                        Output1a.pop(0)
                        posicion.pop(0)
                    if len(peso) > 1000:#limite de puntos que lee del arduino.
                        peso.pop(0)
                        peso2.pop(0)
                        pesoset.pop(0)
            
        except Exception as e:
            print(e)

# Función para iniciar la lectura de datos
def start_reading():
    global running
    running = True
    threading.Thread(target=read_serial_data, daemon=True).start()

# Función para detener la lectura de datos
def stop_reading():
    global running
    global mensaje
    running = False
    if ser:
        ser.close()
        mensaje="Lectura parada"
    messagebox.showinfo("Información", "Lectura de datos detenida y puerto serial cerrado")
    
#Cerrar todo
def salir():
    global running
    global mensaje
    running = False
    if ser:
        ser.close()
        mensaje="Lectura parada"
    root.quit()  # Finaliza el mainloop de Tkinter
    root.destroy()  # Cierra la ventana de la interfaz gráfica  

# Función para enviar comandos al Arduino
def send_command(command):
    try:
        ser.write(command.encode('utf-8'))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Función para actualizar la gráfica
def animate(i):
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax1.plot(SpPosicion, label="SP Posicion")
    ax1.plot(velocidad,label='velocidad mm/s')
    ax1.plot(Output1a, label="CV PWM")
    ax1.plot(posicion,label='posicion mm')
    ax1.set_title("Motor DC elevador")
    
    ax2.plot(peso, label=f'peso={peso_escalar} g')
    ax2.plot(pesoset, label='pesoset')
    ax2.set_title("Pesado del alimento seco")
    
    ax3.plot(peso2, label='peso humedo')
    ax3.plot(peso, label='peso')
    ax3.set_title("Pesado del alimento humedo")
    
    
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')
    ax3.legend(loc='upper right')
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.set_ylim([0, 300])
    ax2.set_ylim([0, 100])
    ax3.set_ylim([0, 100])

#funcion imprimir
def save_to_excel():
    df=pd.DataFrame({'SPposicion':SpPosicion, 'velocidad':velocidad, 'CV':Output1a, 'posicion':posicion, 'peso':peso})
    filename='TesisData.xlsx'
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# Configuración inicial de la interfaz gráfica
root = tk.Tk()
root.title("Interfaz Serial con Arduino")
root.config(bg="gray")


# Variables globales
com_port = tk.StringVar()
baud_rate = tk.StringVar()
estado = tk.StringVar()
running = False
mensaje=""
ser = None
SpPosicion = [] #SP posicion
velocidad = [] #velocidad
Output1a = [] #CV
posicion = [] #posicion
peso = [] #peso
peso2 = []
pesoset = []
peso_escalar=0
peso2_escalar=0

# Frame para la configuración de la conexión serial
frame_config = ttk.LabelFrame(root, text="Configuración Serial")
frame_config.grid(column=0, row=0, padx=10, pady=10, sticky="ew")


ttk.Label(frame_config, text="Puerto COM:").grid(column=0, row=0, padx=5, pady=5)
ttk.Combobox(frame_config, textvariable=com_port, values=get_com_ports()).grid(column=1, row=0, padx=5, pady=5)

ttk.Label(frame_config, text="Baud Rate:").grid(column=0, row=1, padx=5, pady=5)
ttk.Combobox(frame_config, textvariable=baud_rate, values=["9600", "19200", "38400", "57600", "115200"]).grid(column=1, row=1, padx=5, pady=5)

ttk.Button(frame_config, text="Iniciar", command=start_serial_connection).grid(column=0, row=2, columnspan=1, pady=10)
ttk.Button(frame_config, text="Parar", command=stop_reading).grid(column=1, row=2, columnspan=1, pady=10)
ttk.Button(frame_config, text="Guardar Data", command=save_to_excel).grid(column=0, row=3, columnspan=1, pady=10)
ttk.Label(frame_config, text=mensaje).grid(column=1, row=3, padx=5, pady=5)

# Frame para los controles
frame_controls = ttk.LabelFrame(root, text="Controles")
frame_controls.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

ttk.Button(frame_controls, text="Start", command=lambda: send_command('start')).grid(column=0, row=0, padx=5, pady=5)
ttk.Button(frame_controls, text="Stop", command=lambda: send_command('Stop')).grid(column=1, row=0, padx=5, pady=5)
#ttk.Button(frame_controls, text="PE", command=lambda: send_command('PE')).grid(column=2, row=0, padx=5, pady=5)


# Frame para mostrar el estado
frame_status = ttk.LabelFrame(root, text="Estado")
frame_status.grid(column=0, row=2, padx=10, pady=10, sticky="ew")

ttk.Label(frame_status, text=f'estado={estado}', font=15).grid(column=0, row=0, padx=5, pady=5)

# Frame para mostrar el Salir
frame_salir = ttk.LabelFrame(root, text="Salir")
frame_salir.grid(column=0, row=3, padx=10, pady=10, sticky="ew")

font_style = ("Helvetica", 16, "bold")

ttk.Button(frame_salir, text="Salir", command=salir).grid(column=0, row=0, columnspan=1, pady=10)


# Configuración de la gráfica
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,9))
fig.tight_layout(pad=3.0) #agrega una separacion entre figuras.
ani = animation.FuncAnimation(fig, animate, interval=100)

# Frame para la gráfica
frame_graph = ttk.LabelFrame(root, text="Gráfica en Tiempo Real")
frame_graph.grid(column=1, row=0, rowspan=4, padx=10, pady=10, sticky="ns")


canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Ejecución del mainloop de Tkinter
root.mainloop()
