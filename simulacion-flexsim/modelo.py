"""Réplica en Python (SimPy) del modelo FlexSim "Problema de simulación".

Se usa para obtener las mismas estadísticas que entrega el reporte de FlexSim
(entradas, salidas, utilización, colas, tiempos de ciclo) y para evaluar la
propuesta de mejora. Horizonte: 480 min (un turno de 8 h). Tiempos en minutos.

Supuestos (ver informe):
  * Source A: llegadas exponenciales, media 2.
  * Source B: paquetes de 3 uds., llegadas exponenciales, media 7 min entre paquetes.
  * Acondicionado 1: triangular(min=1, moda=4, max=8)   (FlexSim: triangular(1,4,8,0))
  * Acondicionado 2: triangular(min=2, moda=4, max=8)
  * Lotificado: A -> normal(media=1, desv=0.2); B -> lognormal2(loc=0, escala=2.5, forma=0.5)
  * 5 % defectuosos -> Reproceso (5 min constantes) -> 60 % pasa / 40 % a basura.
  * Colas de capacidad infinita, un solo operador por estación (caso base).
"""
import math
import random
from dataclasses import dataclass, field

import numpy as np
import simpy

HORIZONTE = 480.0


@dataclass
class Estacion:
    nombre: str
    servidores: int = 1
    entradas: int = 0
    salidas: int = 0
    tiempo_ocupado: float = 0.0
    espera_total: float = 0.0
    q_max: int = 0
    q_area: float = 0.0
    _q_t: float = 0.0
    _q_len: int = 0
    res: simpy.Resource = None
    serie_cola: list = field(default_factory=list)

    def cola_cambia(self, t, nuevo):
        self.q_area += self._q_len * (t - self._q_t)
        self._q_t, self._q_len = t, nuevo
        self.q_max = max(self.q_max, nuevo)

    def utilizacion(self, T=HORIZONTE):
        return self.tiempo_ocupado / (T * self.servidores)

    def cola_media(self, T=HORIZONTE):
        return (self.q_area + self._q_len * (T - self._q_t)) / T

    def espera_media(self):
        return self.espera_total / self.salidas_iniciadas if self.salidas_iniciadas else 0.0

    salidas_iniciadas: int = 0


def simular(semilla=1, n_acond1=1, n_acond2=1, n_lotif=1, n_reproc=1, T=HORIZONTE):
    rnd = random.Random(semilla)
    rng = np.random.default_rng(semilla)
    env = simpy.Environment()

    est = {
        "acond1": Estacion("Acondicionado 1", n_acond1),
        "acond2": Estacion("Acondicionado 2", n_acond2),
        "lotif": Estacion("Lotificado", n_lotif),
        "reproc": Estacion("Reproceso", n_reproc),
    }
    for e in est.values():
        e.res = simpy.Resource(env, capacity=e.servidores)

    src = {"A": 0, "B_paquetes": 0, "B": 0}
    out = {"almacen": 0, "basura": 0, "almacen_lotif": 0, "almacen_reproc": 0,
           "almacen_A": 0, "almacen_B": 0, "basura_A": 0, "basura_B": 0}
    ciclos = {"A": [], "B": []}  # tiempo total en sistema de piezas terminadas
    trabajo = {"n": 0}  # piezas creadas

    def tiempo_proceso(clave, tipo):
        if clave == "acond1":
            return rnd.triangular(1, 8, 4)
        if clave == "acond2":
            return rnd.triangular(2, 8, 4)
        if clave == "lotif":
            if tipo == "A":
                return max(0.0, rnd.gauss(1.0, 0.2))
            return float(rng.lognormal(mean=math.log(2.5), sigma=0.5))
        if clave == "reproc":
            return 5.0

    def pasar(clave, tipo):
        e = est[clave]
        t0 = env.now
        e.entradas += 1
        e.cola_cambia(env.now, e._q_len + 1)
        with e.res.request() as req:
            yield req
            e.cola_cambia(env.now, e._q_len - 1)
            e.espera_total += env.now - t0
            e.salidas_iniciadas += 1
            d = tiempo_proceso(clave, tipo)
            # solo se contabiliza el tiempo de proceso dentro del horizonte
            e.tiempo_ocupado += max(0.0, min(env.now + d, T) - env.now)
            yield env.timeout(d)
            e.salidas += 1

    def pieza(tipo, t_creacion):
        trabajo["n"] += 1
        yield env.process(pasar("acond1" if tipo == "A" else "acond2", tipo))
        yield env.process(pasar("lotif", tipo))
        if rnd.random() < 0.05:                      # defecto de impresión
            yield env.process(pasar("reproc", tipo))
            if rnd.random() < 0.60:
                out["almacen"] += 1; out["almacen_reproc"] += 1
                out["almacen_" + tipo] += 1
                ciclos[tipo].append(env.now - t_creacion)
            else:
                out["basura"] += 1; out["basura_" + tipo] += 1
        else:
            out["almacen"] += 1; out["almacen_lotif"] += 1
            out["almacen_" + tipo] += 1
            ciclos[tipo].append(env.now - t_creacion)

    def fuente_A():
        while True:
            yield env.timeout(rnd.expovariate(1 / 2.0))
            src["A"] += 1
            env.process(pieza("A", env.now))

    def fuente_B():
        while True:
            yield env.timeout(rnd.expovariate(1 / 7.0))
            src["B_paquetes"] += 1
            for _ in range(3):               # el paquete se separa en 3 piezas
                src["B"] += 1
                env.process(pieza("B", env.now))

    def monitor():
        while True:
            for k, e in est.items():
                e.serie_cola.append((env.now, e._q_len, e.res.count))
            yield env.timeout(1.0)

    env.process(fuente_A()); env.process(fuente_B()); env.process(monitor())
    env.run(until=T)

    wip = {k: e._q_len + e.res.count for k, e in est.items()}
    return dict(est=est, src=src, out=out, ciclos=ciclos, wip=wip, T=T)


def replicar(n=30, **kw):
    return [simular(semilla=s, **kw) for s in range(1, n + 1)]


if __name__ == "__main__":
    r = simular(1)
    for k, e in r["est"].items():
        print(k, e.entradas, e.salidas, round(e.utilizacion(), 3), round(e.cola_media(), 1), e.q_max)
    print(r["src"], r["out"])
