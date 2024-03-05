import simpy
import numpy as np
import random
import matplotlib.pyplot as plt

# Constantes
MEMORIA_FIJA = 100
CPU = 2
random_seed = 100
REQ_CPU = 20
INSTRUCCIONES_POR_TIEMPO = 1
class Programa:
    def __init__(self, nombre, entorno, memoria_ram, procesador):
        self.nombre = nombre
        self.memoria = np.random.randint(1, 10)
        self.num_instrucciones = np.random.randint(1, 10)
        self.entorno = entorno 
        self.memoria_ram = memoria_ram 
        self.procesador = procesador

    def imprimir_salida(self, mensaje):
        print(f"{self.nombre} {mensaje}")

    def pedir_memoria(self):
        self.imprimir_salida(f"está pidiendo {self.memoria} de memoria.")
        yield self.memoria_ram.get(self.memoria)

    def usar_cpu(self):
        self.imprimir_salida("está solicitando el CPU.")
        with self.procesador.request() as req:
            yield req

            while self.num_instrucciones > 0:
                yield self.entorno.timeout(1)
                self.num_instrucciones -= INSTRUCCIONES_POR_TIEMPO

    def pedir_io(self):
        self.imprimir_salida("está solicitando I/O")
        yield self.entorno.timeout(2)

    def run(self, Memoria):
        inicio = self.entorno.now
        self.imprimir_salida("está corriendo")
        yield self.entorno.process(self.pedir_memoria())
        while self.num_instrucciones > 0:
            yield self.entorno.timeout(1)
            yield self.entorno.process(self.usar_cpu())

        if np.random.randint(1, 2) == 1:
            yield self.entorno.process(self.pedir_io())

        self.imprimir_salida(f"está liberando {self.memoria} de memoria.")
        yield self.memoria_ram.put(self.memoria)
        Memoria.append(self.entorno.now)

def simular_ciclos(numero_procesos, entorno, memoria_ram, cpu, Memoria):
    for i in range(numero_procesos):
        nombre_tarea = f"tarea-{i}"
        nuevo_proceso = Programa(nombre_tarea, entorno, memoria_ram, cpu)
        entorno.process(nuevo_proceso.run(Memoria))
        yield entorno.timeout(random.expovariate(0.1))

# Inicialización
random.seed(random_seed)
entorno = simpy.Environment()
RAM = simpy.Container(entorno, capacity=MEMORIA_FIJA, init=MEMORIA_FIJA)
CPU = simpy.Resource(entorno, capacity=CPU)

print("Comenzando simulación")

# Simulación para diferentes valores de procesos
valores_procesos = [25, 50, 100, 150, 200]
tiempos_totales = []

for cantidad_procesos in valores_procesos:
    Memoria = []
    entorno.process(simular_ciclos(cantidad_procesos, entorno, RAM, CPU, Memoria))
    entorno.run()
    tiempos_totales.append(Memoria)

# Cálculos y gráfico
tiempos_promedio = [np.mean(tiempos) for tiempos in tiempos_totales]
desviaciones_estandar = [np.std(tiempos) for tiempos in tiempos_totales]

# Crear gráfico con Matplotlib
plt.fill_between(valores_procesos, 0, tiempos_promedio, alpha=0.2, color='red')
plt.plot(valores_procesos, tiempos_promedio, marker='o', label='Tiempo Promedio' ,color="red")
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo Promedio ')
plt.title('Tiempo Promedio / Número de Procesos')
plt.legend()
plt.grid(True)
plt.show()
