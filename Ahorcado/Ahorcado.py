import random
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas

# Palabras por temática
tematicas = {
    "frutas": ["manzana", "platano", "cereza", "fresa", "naranja"],
    "conceptos informáticos": ["variable", "función", "algoritmo", "compilador", "bucle"],
    "nombres de personas": ["andrea", "carlos", "maria", "juan", "laura"]
}

# Cargar o inicializar el registro de partidas
try:
    with open("registro_partidas.json", "r") as file:
        registro_partidas = json.load(file)
except FileNotFoundError:
    registro_partidas = {}

def guardar_registro():
    with open("registro_partidas.json", "w") as file:
        json.dump(registro_partidas, file)

def elegir_palabra(tematica):
    return random.choice(tematicas[tematica])

class AhorcadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego del Ahorcado")
        self.root.geometry("600x900")
        self.root.configure(bg="#f0f0f0")
        
        self.jugador = ""
        self.palabra = ""
        self.palabra_oculta = []
        self.intentos_restantes = 6
        self.letras_intentadas = []

        self.setup_inicio()

    def setup_inicio(self):
        self.limpiar_ventana()

        titulo = tk.Label(self.root, text="Bienvenido al juego del Ahorcado!", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        titulo.pack(pady=20)

        tk.Label(self.root, text="Ingresa tu nombre:", font=("Helvetica", 14), bg="#f0f0f0").pack(pady=10)
        
        self.nombre_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.nombre_entry.pack(pady=10)
        
        tk.Button(self.root, text="Comenzar", font=("Helvetica", 14), command=self.iniciar_juego, bg="#4CAF50", fg="white", width=15).pack(pady=20)

    def iniciar_juego(self):
        self.jugador = self.nombre_entry.get().lower()
        if not self.jugador:
            messagebox.showwarning("Advertencia", "Por favor, ingresa tu nombre.")
            return
        
        self.seleccionar_tematica()

    def seleccionar_tematica(self):
        self.limpiar_ventana()
        
        tk.Label(self.root, text="Elige una temática:", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=20)
        for tematica in tematicas.keys():
            tk.Button(self.root, text=tematica.capitalize(), font=("Helvetica", 14), command=lambda t=tematica: self.comenzar_juego(t), bg="#2196F3", fg="white", width=20).pack(pady=10)

    def comenzar_juego(self, tematica):
        self.palabra = elegir_palabra(tematica)
        self.palabra_oculta = ["_" for _ in self.palabra]
        self.intentos_restantes = 6
        self.letras_intentadas = []
        
        self.mostrar_juego()

    def mostrar_juego(self):
        self.limpiar_ventana()

        # Canvas para el monigote
        self.canvas = Canvas(self.root, width=300, height=300, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.dibujar_monigote()

        self.palabra_label = tk.Label(self.root, text=" ".join(self.palabra_oculta), font=("Helvetica", 20, "bold"), bg="#f0f0f0")
        self.palabra_label.pack(pady=10)
        
        self.intentos_label = tk.Label(self.root, text=f"Intentos restantes: {self.intentos_restantes}", font=("Helvetica", 14), bg="#f0f0f0")
        self.intentos_label.pack(pady=5)
        
        self.letras_label = tk.Label(self.root, text=f"Letras intentadas: {', '.join(self.letras_intentadas)}", font=("Helvetica", 14), bg="#f0f0f0")
        self.letras_label.pack(pady=5)
        
        self.letra_entry = tk.Entry(self.root, font=("Helvetica", 14), width=5)
        self.letra_entry.pack(pady=5)
        
        tk.Button(self.root, text="Adivinar letra", font=("Helvetica", 14), command=self.adivinar_letra, bg="#FF9800", fg="white", width=15).pack(pady=5)
        
        tk.Label(self.root, text="O intenta adivinar la palabra completa:", font=("Helvetica", 14, "italic"), bg="#f0f0f0").pack(pady=5)
        self.palabra_entry = tk.Entry(self.root, font=("Helvetica", 14), width=20)
        self.palabra_entry.pack(pady=5)
        
        tk.Button(self.root, text="Adivinar palabra", font=("Helvetica", 14), command=self.adivinar_palabra, bg="#FF5722", fg="white", width=15).pack(pady=5)

    def dibujar_monigote(self):
        # Dibujar el monigote según los intentos restantes
        self.canvas.delete("all")
        if self.intentos_restantes <= 5:
            # Base
            self.canvas.create_line(10, 290, 290, 290, width=5)
        if self.intentos_restantes <= 4:
            # Poste
            self.canvas.create_line(50, 290, 50, 20, width=5)
        if self.intentos_restantes <= 3:
            # Barra superior
            self.canvas.create_line(50, 20, 200, 20, width=5)
            self.canvas.create_line(200, 20, 200, 50, width=5)  # Cuerda
        if self.intentos_restantes <= 2:
            # Cabeza
            self.canvas.create_oval(180, 50, 220, 90, width=5)
        if self.intentos_restantes <= 1:
            # Cuerpo
            self.canvas.create_line(200, 90, 200, 170, width=5)
        if self.intentos_restantes == 0:
            # Brazos y piernas
            self.canvas.create_line(200, 110, 170, 140, width=5)  # Brazo izquierdo
            self.canvas.create_line(200, 110, 230, 140, width=5)  # Brazo derecho
            self.canvas.create_line(200, 170, 170, 210, width=5)  # Pierna izquierda
            self.canvas.create_line(200, 170, 230, 210, width=5)  # Pierna derecha

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

        if self.jugador not in registro_partidas:
            registro_partidas[self.jugador] = {"ganadas": 0, "perdidas": 0}
        if resultado == "ganado":
            registro_partidas[self.jugador]["ganadas"] += 1
        else:
            registro_partidas[self.jugador]["perdidas"] += 1

        guardar_registro()
        self.mostrar_estadisticas()

    def mostrar_estadisticas(self):
        self.limpiar_ventana()

        ganadas = registro_partidas[self.jugador]["ganadas"]
        perdidas = registro_partidas[self.jugador]["perdidas"]
        
        tk.Label(self.root, text=f"{self.jugador.capitalize()}, has ganado {ganadas} partidas y perdido {perdidas}.", font=("Helvetica", 16), bg="#f0f0f0").pack(pady=20)
        tk.Button(self.root, text="Jugar de nuevo", font=("Helvetica", 14), command=self.setup_inicio, bg="#4CAF50", fg="white", width=15).pack(pady=20)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AhorcadoApp(root)
    root.mainloop()
