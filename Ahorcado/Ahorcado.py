import random
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas
from tkinter import PhotoImage
import atexit

# Conectar la base de datos
conn = sqlite3.connect('ahorcado.db')
c = conn.cursor()

# Crear la tabla
c.execute('''
    CREATE TABLE IF NOT EXISTS jugadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        ganadas INTEGER DEFAULT 0,
        perdidas INTEGER DEFAULT 0
    )
''')
conn.commit()

def cerrar_conexion():
    if conn:
        conn.close()

atexit.register(cerrar_conexion)

def guardar_jugador(nombre, resultado):
    c.execute("SELECT * FROM jugadores WHERE nombre = ?", (nombre,))
    jugador = c.fetchone()

    if jugador:
        if resultado == "ganado":
            c.execute("UPDATE jugadores SET ganadas = ganadas + 1 WHERE nombre = ?", (nombre,))
        elif resultado == "perdido":
            c.execute("UPDATE jugadores SET perdidas = perdidas + 1 WHERE nombre = ?", (nombre,))
    else:
        try:
            if resultado == "ganado":
                c.execute("INSERT INTO jugadores (nombre, ganadas, perdidas) VALUES (?, 1, 0)", (nombre,))
            elif resultado == "perdido":
                c.execute("INSERT INTO jugadores (nombre, ganadas, perdidas) VALUES (?, 0, 1)", (nombre,))
        except sqlite3.IntegrityError as e:
            print(f"Error al insertar el jugador: {e}")

    conn.commit()
    print("Datos guardados correctamente.")

def obtener_estadisticas(nombre):
    c.execute("SELECT ganadas, perdidas FROM jugadores WHERE nombre = ?", (nombre,))
    jugador = c.fetchone()
    return jugador if jugador else (0, 0)

def elegir_palabra(tematica):
    tematicas = {
        "frutas": ["manzana", "platano", "cereza", "fresa", "naranja", "mango", "melon", "sandia"],
        "conceptos informáticos": ["variable", "función", "algoritmo", "compilador", "bucle"],
        "nombres de personas": ["andrea", "carlos", "maria", "juan", "laura", "antonio", "paco", "ana"]
    }
    return random.choice(tematicas[tematica])

class AhorcadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego del Ahorcado")
        self.root.geometry("650x950")
        
        # Añadir imagen de fondo
        self.background_image = PhotoImage(file="fondo.png")
        self.background_label = tk.Label(self.root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)
        self.background_label.lower()
        
        self.jugador = ""
        self.palabra = ""
        self.palabra_oculta = []
        self.intentos_restantes = 6
        self.letras_intentadas = []

        self.setup_inicio()

    def setup_inicio(self):
        self.limpiar_ventana()

        titulo = tk.Label(self.root, text="Bienvenido al juego del Ahorcado!", font=("Helvetica", 28, "bold"), bg="#e6e6fa", fg="#333366")
        titulo.pack(pady=30)

        tk.Label(self.root, text="Ingresa tu nombre:", font=("Helvetica", 16), bg="#e6e6fa").pack(pady=10)
        
        self.nombre_entry = tk.Entry(self.root, font=("Helvetica", 16), width=30)
        self.nombre_entry.pack(pady=10)
        
        tk.Button(self.root, text="Comenzar", font=("Helvetica", 16), command=self.iniciar_juego, bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def iniciar_juego(self):
        self.jugador = self.nombre_entry.get().strip().lower()
        if not self.jugador:
            messagebox.showwarning("Advertencia", "Por favor, ingresa tu nombre.")
            return
        
        ganadas, perdidas = obtener_estadisticas(self.jugador)
        messagebox.showinfo("Estadísticas", f"{self.jugador.capitalize()}, has ganado {ganadas} partidas y perdido {perdidas}.")
        
        self.seleccionar_tematica()

    def seleccionar_tematica(self):
        self.limpiar_ventana()
        
        tk.Label(self.root, text="Elige una temática:", font=("Helvetica", 20, "bold"), bg="#e6e6fa", fg="#333366").pack(pady=30)
        for tematica in ["frutas", "conceptos informáticos", "nombres de personas"]:
            tk.Button(self.root, text=tematica.capitalize(), font=("Helvetica", 16), command=lambda t=tematica: self.comenzar_juego(t), bg="#2196F3", fg="white", width=25).pack(pady=15)

    def comenzar_juego(self, tematica):
        self.palabra = elegir_palabra(tematica)
        self.palabra_oculta = ["_" for _ in self.palabra]
        self.intentos_restantes = 6
        self.letras_intentadas = []
        
        self.mostrar_juego()

    def mostrar_juego(self):
        self.limpiar_ventana()

        # Canvas para el monigote
        self.canvas = Canvas(self.root, width=400, height=400, bg="#e6e6fa", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.dibujar_monigote()

        self.palabra_label = tk.Label(self.root, text=" ".join(self.palabra_oculta), font=("Helvetica", 24, "bold"), bg="#e6e6fa", fg="#333366")
        self.palabra_label.pack(pady=20)
        
        self.intentos_label = tk.Label(self.root, text=f"Intentos restantes: {self.intentos_restantes}", font=("Helvetica", 16), bg="#e6e6fa", fg="#800000")
        self.intentos_label.pack(pady=10)
        
        self.letras_label = tk.Label(self.root, text=f"Letras intentadas: {', '.join(self.letras_intentadas)}", font=("Helvetica", 16), bg="#e6e6fa", fg="#800000")
        self.letras_label.pack(pady=10)
        
        self.letra_entry = tk.Entry(self.root, font=("Helvetica", 16), width=5)
        self.letra_entry.pack(pady=10)
        
        tk.Button(self.root, text="Adivinar letra", font=("Helvetica", 16), command=self.adivinar_letra, bg="red", fg="white", width=20).pack(pady=10)
        
        tk.Label(self.root, text="Intenta adivinar la palabra completa:", font=("Helvetica", 16, "italic"), bg="#e6e6fa", fg="#333366").pack(pady=10)
        self.palabra_entry = tk.Entry(self.root, font=("Helvetica", 16), width=25)
        self.palabra_entry.pack(pady=10)
        
        tk.Button(self.root, text="Adivinar palabra", font=("Helvetica", 16), command=self.adivinar_palabra, bg="black", fg="white", width=20).pack(pady=10)

    def dibujar_monigote(self):
        # Dibujar el monigote según los intentos restantes
        self.canvas.delete("all")
        if self.intentos_restantes <= 5:
            # Base
            self.canvas.create_line(10, 390, 390, 390, width=5)
        if self.intentos_restantes <= 4:
            # Poste
            self.canvas.create_line(50, 390, 50, 20, width=5)
        if self.intentos_restantes <= 3:
            # Barra superior
            self.canvas.create_line(50, 20, 250, 20, width=5)
            self.canvas.create_line(250, 20, 250, 70, width=5)  # Cuerda
        if self.intentos_restantes <= 2:
            # Cabeza
            self.canvas.create_oval(230, 70, 270, 110, width=5)
        if self.intentos_restantes <= 1:
            # Cuerpo05070
            self.canvas.create_line(250, 110, 250, 250, width=5)
        if self.intentos_restantes == 0:
            # Brazos y piernas
            self.canvas.create_line(250, 150, 220, 200, width=5)  # Brazo izquierdo
            self.canvas.create_line(250, 150, 280, 200, width=5)  # Brazo derecho
            self.canvas.create_line(250, 250, 220, 320, width=5)  # Pierna izquierda
            self.canvas.create_line(250, 250, 280, 320, width=5)  # Pierna derecha

    def adivinar_letra(self):
        letra = self.letra_entry.get().lower()
        self.letra_entry.delete(0, tk.END)
        
        if not letra or len(letra) != 1 or not letra.isalpha():
            messagebox.showwarning("Advertencia", "Por favor, ingresa una letra válida.")
            return

        if letra in self.letras_intentadas:
            messagebox.showinfo("Información", "Ya intentaste esa letra. Prueba con otra.")
            return

        self.letras_intentadas.append(letra)

        if letra in self.palabra:
            for i, l in enumerate(self.palabra):
                if l == letra:
                    self.palabra_oculta[i] = letra
            self.palabra_label.config(text=" ".join(self.palabra_oculta))
            if "_" not in self.palabra_oculta:
                self.terminar_juego(True)
        else:
            self.intentos_restantes -= 1
            self.intentos_label.config(text=f"Intentos restantes: {self.intentos_restantes}")
            self.dibujar_monigote()
            if self.intentos_restantes == 0:
                self.terminar_juego(False)

        self.letras_label.config(text=f"Letras intentadas: {', '.join(self.letras_intentadas)}")

    def adivinar_palabra(self):
        palabra_intento = self.palabra_entry.get().lower()
        self.palabra_entry.delete(0, tk.END)
        
        if not palabra_intento or not palabra_intento.isalpha():
            messagebox.showwarning("Advertencia", "Por favor, ingresa una palabra válida.")
            return

        if palabra_intento == self.palabra:
            self.terminar_juego(True)
        else:
            self.intentos_restantes -= 1
            self.intentos_label.config(text=f"Intentos restantes: {self.intentos_restantes}")
            self.dibujar_monigote()
            if self.intentos_restantes == 0:
                self.terminar_juego(False)

    def terminar_juego(self, ganado):
        if ganado:
            messagebox.showinfo("¡Felicidades!", f"Has adivinado la palabra: {self.palabra}")
            resultado = "ganado"
        else:
            messagebox.showinfo("Fin del juego", f"Te has quedado sin intentos. La palabra era: {self.palabra}")
            resultado = "perdido"

        guardar_jugador(self.jugador, resultado)
        self.mostrar_estadisticas()

    def mostrar_estadisticas(self):
        self.limpiar_ventana()

        ganadas, perdidas = obtener_estadisticas(self.jugador)
        
        tk.Label(self.root, text=f"{self.jugador.capitalize()}, has ganado {ganadas} partidas y perdido {perdidas}.", font=("Helvetica", 20), bg="#e6e6fa", fg="#333366").pack(pady=30)
        tk.Button(self.root, text="Jugar de nuevo", font=("Helvetica", 16), command=self.setup_inicio, bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            if widget != self.background_label:
                widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AhorcadoApp(root)
    root.mainloop()
