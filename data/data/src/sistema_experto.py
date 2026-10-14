import json
import os

class MotorInferencia:
    def __init__(self):
        self.memoria_trabajo = {}
        self.base_conocimiento = []
        self.reglas_activadas = set()
        self.pasos_inferencia = []

    def cargar_base_conocimiento(self, ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            self.base_conocimiento = json.load(f)

    def cargar_hechos_iniciales(self, ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            self.memoria_trabajo = json.load(f)

    def evaluar_condicion(self, ant):
        var = ant['variable']
        op = ant['operador']
        val_esperado = ant['valor']

        if var not in self.memoria_trabajo:
            return False

        val_actual = self.memoria_trabajo[var]

        if op == "==": return val_actual == val_esperado
        if op == "!=": return val_actual != val_esperado
        if op == ">":  return float(val_actual) > float(val_esperado)
        if op == "<":  return float(val_actual) < float(val_esperado)
        if op == ">=": return float(val_actual) >= float(val_esperado)
        if op == "<=": return float(val_actual) <= float(val_esperado)
        return False

    def resolver_conflictos(self, conjunto_conflicto):
        return sorted(
            conjunto_conflicto,
            key=lambda r: (r.get('prioridad', 0), len(r['antecedentes'])),
            reverse=True
        )

    def ejecutar(self):
        self.pasos_inferencia = []
        self.reglas_activadas = set()
        ciclo = 1

        while True:
            conjunto_conflicto = []

            for regla in self.base_conocimiento:
                if regla['id'] in self.reglas_activadas:
                    continue

                cumple = all(self.evaluar_condicion(ant) for ant in regla['antecedentes'])
                if cumple:
                    conjunto_conflicto.append(regla)

            if not conjunto_conflicto:
                break

            reglas_ordenadas = self.resolver_conflictos(conjunto_conflicto)
            regla_disparada = reglas_ordenadas[0]

            self.reglas_activadas.add(regla_disparada['id'])
            nuevos_hechos = []

            for cons in regla_disparada['consecuentes']:
                self.memoria_trabajo[cons['variable']] = cons['valor']
                nuevos_hechos.append(f"{cons['variable']} = {cons['valor']}")

            self.pasos_inferencia.append({
                "ciclo": ciclo,
                "regla": regla_disparada['id'],
                "nuevos_hechos": nuevos_hechos,
                "memoria_actual": dict(self.memoria_trabajo)
            })

            ciclo += 1


def interfaz_consola():
    motor = MotorInferencia()
    print("=" * 60)
    print("  SISTEMA EXPERTO DE DIAGNÓSTICO DE REDES Y SERVIDORES")
    print("=" * 60)

    archivo_bc = input("Ruta de la Base de Conocimiento [defecto: data/reglas.json]: ") or "data/reglas.json"
    motor.cargar_base_conocimiento(archivo_bc)

    print("\nModo de ingreso de hechos iniciales:")
    print("1. Cargar desde archivo JSON")
    print("2. Ingreso interactivo por consola")
    opc = input("Seleccione una opción (1/2): ")

    if opc == "1":
        archivo_hechos = input("Ruta de hechos iniciales [defecto: data/hechos_caso1.json]: ") or "data/hechos_caso1.json"
        motor.cargar_hechos_iniciales(archivo_hechos)
    else:
        print("\nIngrese las variables conocidas (deje el nombre vacío para terminar):")
        while True:
            var = input(" Nombre de variable (ej. ping_gateway): ").strip()
            if not var: break
            val = input(f" Valor para '{var}': ").strip()
            if val.isdigit(): val = int(val)
            motor.memoria_trabajo[var] = val

    print("\n" + "=" * 60)
    print(" EJECUTANDO MOTOR DE INFERENCIA (FORWARD CHAINING)")
    print("=" * 60)

    motor.ejecutar()

    for paso in motor.pasos_inferencia:
        print(f"\n[CICLO {paso['ciclo']}] Disparada Regla: {paso['regla']}")
        print(f" -> Nuevos Hechos Deducidos: {', '.join(paso['nuevos_hechos'])}")

    print("\n" + "=" * 60)
    print(" RECOMENDACIÓN / DIAGNÓSTICO FINAL")
    print("=" * 60)

    if "recomendacion" in motor.memoria_trabajo:
        print(f" R/ {motor.memoria_trabajo['recomendacion']}")
    else:
        print(" No se alcanzó una recomendación definitiva con los hechos proporcionados.")

if __name__ == "__main__":
    interfaz_consola()
