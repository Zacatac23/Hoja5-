import simpy
import random

# Semilla para reproducibilidad
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Parámetros de la simulación
INTERVALO_CREACION_PROCESOS = 10
CANTIDAD_PROCESOS = [50]
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Número de instrucciones que puede ejecutar el CPU en una unidad de tiempo

# Variables para almacenar los tiempos de ejecución de los procesos
tiempos_ejecucion = {i: [] for i in range(1, max(CANTIDAD_PROCESOS) + 1)}

# Definición del ambiente de simulación
env = simpy.Environment()

# Recurso para modelar la memoria RAM
RAM = simpy.Container(env, init=MEMORIA_RAM, capacity=MEMORIA_RAM)

# Cola de procesos en estado "new"
cola_nuevos_procesos = simpy.Store(env)

# Cola de procesos en estado "waiting" (I/O)
cola_waiting = simpy.Store(env)

# Cola de procesos en estado "ready"
cola_ready = simpy.Store(env)

# Recurso para modelar el CPU
cpu = simpy.Resource(env, capacity=1)

# Función para la llegada de procesos
def llegada_procesos(env, num_procesos):
    for i in range(num_procesos):
        yield env.timeout(random.expovariate(1.0 / INTERVALO_CREACION_PROCESOS))
        proceso = procesar_proceso(env, i + 1)
        env.process(proceso)

# Función para procesar un proceso
def procesar_proceso(env, id_proceso):
    memoria_requerida = random.randint(1, 10)
    instrucciones_totales = random.randint(1, 10)
    instrucciones_restantes = instrucciones_totales

    # Estado "new"
    with RAM.get(memoria_requerida) as req:
        yield req
        llegada = env.now
        cola_nuevos_procesos.put((id_proceso, llegada, memoria_requerida))

    # Estado "ready"
    cola_ready.put((id_proceso, instrucciones_restantes))

    # Estado "running"
    with cpu.request() as req:
        yield req
        while instrucciones_restantes > 0:
            yield env.timeout(1)
            instrucciones_restantes -= VELOCIDAD_CPU
        if instrucciones_restantes <= 0:
            finalizacion = env.now
            # Determinar el siguiente estado (Terminated, Waiting o Ready)
            siguiente_estado = determinar_siguiente_estado(env)
            if siguiente_estado == "Terminated":
                tiempos_ejecucion[id_proceso].append(finalizacion - llegada)
                RAM.put(memoria_requerida)
            elif siguiente_estado == "Waiting":
                cola_waiting.put((id_proceso, finalizacion))
            elif siguiente_estado == "Ready":
                cola_ready.put((id_proceso, instrucciones_restantes))

# Función para determinar el siguiente estado del proceso
def determinar_siguiente_estado(env):
    probabilidad = random.randint(1, 21)
    if probabilidad == 1:
        return "Waiting"
    elif probabilidad == 2:
        return "Ready"
    else:
        return "Terminated"

# Ejecutar la simulación con diferentes cantidades de procesos
for cantidad_procesos in CANTIDAD_PROCESOS:
    env.process(llegada_procesos(env, cantidad_procesos))
    env.run()

    # Mostrar resultados
    print(f"Resultados para {cantidad_procesos} procesos:")
    for id_proceso in range(1, cantidad_procesos + 1):
        if len(tiempos_ejecucion[id_proceso]) > 0:
            tiempo_ejecucion = tiempos_ejecucion[id_proceso][0]  # Tomar solo el primer tiempo de ejecución
            print(f"Proceso {id_proceso}: Tiempo en la computadora = {tiempo_ejecucion} unidades de tiempo")
        else:
            print(f"Proceso {id_proceso}: No se completó la ejecución.")
    print()