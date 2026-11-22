import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
from modelo import simular, replicar

D = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(D, "img"); os.makedirs(IMG, exist_ok=True)
NREP = 30
CFG = {
    "Base (1-1-1-1)": {},
    "Mejora 1 (3 acond. por línea)": dict(n_acond1=3, n_acond2=3),
    "Mejora 2 (3-3-2 + reproceso 1)": dict(n_acond1=3, n_acond2=3, n_lotif=2),
}
base = simular(1)
reps = {k: replicar(NREP, **v) for k, v in CFG.items()}
mejor = simular(1, n_acond1=3, n_acond2=3, n_lotif=2)

def m(rs, f): return float(np.mean([f(r) for r in rs]))
def ic(rs, f):
    x = np.array([f(r) for r in rs]); return 1.96 * x.std(ddof=1) / np.sqrt(len(x))
def ciclo(r, t=None):
    c = r["ciclos"]["A"] + r["ciclos"]["B"] if t is None else r["ciclos"][t]
    return float(np.mean(c)) if c else 0.0

AZ, NA, VE, RO, GR = "#1f4e79", "#e08a1e", "#2e8b57", "#c0392b", "#7f8c8d"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# ---------- Gráficas del dashboard ----------
nom = ["Acond. 1", "Acond. 2", "Lotificado", "Reproceso"]; ks = ["acond1", "acond2", "lotif", "reproc"]
fig, ax = plt.subplots(figsize=(5.2, 3.2))
u = [base["est"][k].utilizacion() * 100 for k in ks]
b = ax.bar(nom, u, color=[RO if x > 95 else (NA if x > 70 else VE) for x in u])
ax.axhline(85, ls="--", c=GR, lw=1); ax.set_ylabel("Utilización (%)"); ax.set_ylim(0, 115)
ax.set_title("1. Utilización por estación (turno de 480 min)")
for r_, v in zip(b, u): ax.text(r_.get_x() + r_.get_width() / 2, v + 2, f"{v:.1f}%", ha="center")
fig.tight_layout(); fig.savefig(f"{IMG}/g1.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
for k, n_, c in [("acond1", "Acond. 1", AZ), ("acond2", "Acond. 2", NA), ("lotif", "Lotificado", VE)]:
    s = np.array(base["est"][k].serie_cola); ax.plot(s[:, 0], s[:, 1], label=n_, c=c)
ax.set_xlabel("Tiempo (min)"); ax.set_ylabel("Piezas en cola"); ax.legend(frameon=False)
ax.set_title("2. Evolución de la cola en el turno")
fig.tight_layout(); fig.savefig(f"{IMG}/g2.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
o = base["out"]; x = np.arange(2); w = .35
ax.bar(x - w/2, [o["almacen_A"], o["almacen_B"]], w, label="Almacén", color=VE)
ax.bar(x + w/2, [o["basura_A"], o["basura_B"]], w, label="Basura", color=RO)
ax.set_xticks(x, ["Producto A", "Producto B"]); ax.set_ylabel("Piezas"); ax.legend(frameon=False)
for i, (a_, b_) in enumerate([(o["almacen_A"], o["basura_A"]), (o["almacen_B"], o["basura_B"])]):
    ax.text(i - w/2, a_ + 2, a_, ha="center"); ax.text(i + w/2, b_ + 2, b_, ha="center")
ax.set_title("3. Destino final de las piezas")
fig.tight_layout(); fig.savefig(f"{IMG}/g3.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.hist(base["ciclos"]["A"], bins=15, alpha=.7, color=AZ, label="Producto A")
ax.hist(base["ciclos"]["B"], bins=15, alpha=.7, color=NA, label="Producto B")
ax.set_xlabel("Tiempo en el sistema (min)"); ax.set_ylabel("Piezas"); ax.legend(frameon=False)
ax.set_title("4. Tiempo de fabricación (piezas terminadas)")
fig.tight_layout(); fig.savefig(f"{IMG}/g4.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
names = ["Base", "Mejora 1", "Mejora 2"]; vals = [m(reps[k], lambda r: r["out"]["almacen"]) for k in CFG]
errs = [ic(reps[k], lambda r: r["out"]["almacen"]) for k in CFG]
b = ax.bar(names, vals, yerr=errs, capsize=4, color=[GR, NA, VE])
for r_, v in zip(b, vals): ax.text(r_.get_x() + r_.get_width() / 2, v + 12, f"{v:.0f}", ha="center")
ax.set_ylabel("Piezas buenas al almacén"); ax.set_title("5. Producción por escenario (media de 30 réplicas)")
fig.tight_layout(); fig.savefig(f"{IMG}/g5.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
vals = [m(reps[k], lambda r: sum(r["wip"].values())) for k in CFG]
b = ax.bar(names, vals, color=[RO, NA, VE])
for r_, v in zip(b, vals): ax.text(r_.get_x() + r_.get_width() / 2, v + 4, f"{v:.0f}", ha="center")
ax.set_ylabel("Piezas sin terminar al min 480"); ax.set_title("6. Inventario en proceso (WIP) final")
fig.tight_layout(); fig.savefig(f"{IMG}/g6.png", dpi=200); plt.close(fig)

# ---------- PDF ----------
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=colors.HexColor(AZ), fontSize=16, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=colors.HexColor(AZ), fontSize=12, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=9.5, leading=13, alignment=4)
SM = ParagraphStyle("SM", parent=P, fontSize=8, textColor=colors.HexColor("#555555"), alignment=0)
CT = ParagraphStyle("CT", parent=ss["Title"], fontSize=24, textColor=colors.HexColor(AZ))
CS = ParagraphStyle("CS", parent=ss["Normal"], fontSize=12, alignment=1, leading=18)

def tabla(data, widths=None, head=True):
    cs = ParagraphStyle("c", parent=P, fontSize=8.5, leading=10.5, alignment=0)
    ch = ParagraphStyle("h", parent=cs, textColor=colors.white, fontName="Helvetica-Bold")
    data = [[Paragraph(str(c), ch if (i == 0 and head) else cs) for c in row] for i, row in enumerate(data)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    st = [("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#b0b0b0")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6fa")])]
    if head: st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(AZ)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(st)); return t

def panel(titulo, params, res):
    filas = [["PARÁMETROS", "", "RESULTADOS (turno 480 min)", ""]]
    for i in range(max(len(params), len(res))):
        p_ = params[i] if i < len(params) else ("", ""); r_ = res[i] if i < len(res) else ("", "")
        filas.append([p_[0], p_[1], r_[0], r_[1]])
    t = Table(filas, colWidths=[3.6*cm, 4.4*cm, 4.6*cm, 3.6*cm], hAlign="LEFT")
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#b0b0b0")),
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor(AZ)), ("BACKGROUND", (2, 0), (3, 0), colors.HexColor("#2e8b57")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("SPAN", (0, 0), (1, 0)), ("SPAN", (2, 0), (3, 0)), ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"), ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6f8fb"))]))
    return KeepTogether([Paragraph(titulo, H2), t, Spacer(1, 10)])

e = base["est"]; s = base["src"]
def est_res(k):
    x = e[k]
    return [("Entradas", x.entradas), ("Salidas", x.salidas), ("Utilización", f"{x.utilizacion()*100:.1f} %"),
            ("Cola media (pzs)", f"{x.cola_media():.1f}"), ("Cola máxima (pzs)", x.q_max),
            ("Espera media en cola", f"{x.espera_total/max(x.salidas_iniciadas,1):.1f} min"),
            ("Piezas en estación al cierre", base["wip"][k])]

story = []
# Portada
story += [Spacer(1, 3*cm), Paragraph("Simulación de un proceso de producción<br/>con FlexSim", CT), Spacer(1, .6*cm),
          Paragraph("Tiempos de fabricación, cuellos de botella y propuesta de mejora", CS), Spacer(1, 2.5*cm),
          Paragraph("<b>Asignatura:</b> Simulación de procesos<br/><b>Integrantes:</b> [Nombre 1] · [Nombre 2] · [Nombre 3]<br/>"
                    "<b>Docente:</b> [Nombre del docente]<br/><b>Institución:</b> Areandina<br/><b>Fecha:</b> [dd/mm/aaaa]", CS),
          PageBreak()]
# 1
story += [Paragraph("1. Descripción del sistema y supuestos", H1),
 Paragraph("Una empresa fabrica dos productos. El Producto A llega con distribución exponencial (media 2 min) al Acondicionado 1. "
  "El Producto B llega en paquetes de 3 unidades, cada 7 min (exponencial), al Acondicionado 2, donde el paquete se separa en piezas individuales. "
  "Ambos flujos convergen en Lotificado. El 5 % de las piezas sale defectuoso y pasa a Reproceso (5 min constantes); de estas, solo el 60 % aprueba la reinspección. "
  "Las piezas buenas van al almacén de clientes y las demás al cesto de basura. Se simuló un turno de 480 min.", P), Spacer(1, 6),
 tabla([["Estación", "Tiempo de proceso (min)", "Observación"],
  ["Source A", "Exponencial, media 2", "1 pieza por llegada"],
  ["Source B", "Exponencial, media 7", "Paquetes de 3 piezas"],
  ["Acondicionado 1", "Triangular (mín 1, moda 4, máx 8)", "Limpia y etiqueta, solo A"],
  ["Acondicionado 2", "Triangular (mín 2, moda 4, máx 8)", "Separa paquete; solo B"],
  ["Lotificado", "A: Normal(1; 0,2) · B: Lognormal2(0; 2,5; 0,5)", "5 % → Reproceso"],
  ["Reproceso", "Constante 5", "60 % aprueba, 40 % basura"]], [3.5*cm, 7*cm, 5.5*cm]),
 Spacer(1, 8), Paragraph("<b>Supuestos:</b> colas de capacidad infinita y disciplina FIFO; un operador por estación en el caso base; "
  "el parámetro de escala 2,5 de la lognormal se interpretó como exp(μ), de modo que la media es 2,5·e<super>0,5²/2</super> ≈ 2,83 min; "
  "la reinspección es instantánea. Cada escenario se corrió 30 veces con semillas distintas para dar robustez; "
  "los paneles de las secciones 2 a 5 corresponden a la réplica 1 (equivalente a una corrida de FlexSim).", P),
 Spacer(1, 6),
 Paragraph("<b>Nota de reproducibilidad:</b> las cifras de este informe provienen de una réplica del modelo programada en Python (SimPy, archivo modelo.py), "
  "con la misma lógica y parámetros del enunciado. Los paneles de cada estación reproducen los campos del reporte de FlexSim, pero no son capturas de pantalla del programa. "
  "Al correr el modelo en FlexSim (ver Anexo) los números variarán ligeramente por la aleatoriedad; las conclusiones cualitativas no cambian.", SM), PageBreak()]
# 2
story += [Paragraph("2. Parámetros y resultados por estación (6 estaciones)", H1)]
story += [
 panel("2.1 Source A (Producto A)", [("Tipo de llegada", "Intervalo entre llegadas"), ("Distribución", "Exponencial"), ("Media", "2 min"), ("Tipo de ítem", "A")],
       [("Piezas creadas", s["A"]), ("Piezas enviadas", s["A"]), ("Tasa media", f"{s['A']/480:.2f} pzs/min")]),
 panel("2.2 Source B (Producto B, paquetes de 3)", [("Tipo de llegada", "Intervalo entre llegadas"), ("Distribución", "Exponencial"), ("Media", "7 min"), ("Cantidad por llegada", "3 (paquete)")],
       [("Paquetes creados", s["B_paquetes"]), ("Piezas individuales", s["B"]), ("Tasa media", f"{s['B']/480:.2f} pzs/min")]),
 panel("2.3 Acondicionado 1 (Producto A)", [("Distribución", "Triangular"), ("Mínimo / Moda / Máx.", "1 / 4 / 8 min"), ("Media teórica", "4,33 min"), ("Operadores", "1"), ("Capacidad de cola", "Infinita")], est_res("acond1")),
 panel("2.4 Acondicionado 2 (Producto B)", [("Distribución", "Triangular"), ("Mínimo / Moda / Máx.", "2 / 4 / 8 min"), ("Media teórica", "4,67 min"), ("Operadores", "1"), ("Capacidad de cola", "Infinita")], est_res("acond2")),
 panel("2.5 Lotificado (A y B)", [("Producto A", "Normal(1; 0,2)"), ("Producto B", "Lognormal2(0; 2,5; 0,5)"), ("Media teórica A / B", "1,00 / 2,83 min"), ("Operadores", "1"), ("Salida", "95 % almacén / 5 % reproceso")], est_res("lotif")),
 panel("2.6 Reproceso", [("Distribución", "Constante"), ("Tiempo", "5 min"), ("Operadores", "1"), ("Reinspección", "60 % pasa / 40 % basura")], est_res("reproc")),
 PageBreak()]
# 3
story += [Paragraph("3. Cuellos de botella", H1),
 Paragraph("Un cuello de botella aparece donde la demanda de trabajo supera la capacidad. La carga ofrecida (tiempo medio de proceso × tasa de llegada) lo muestra antes de simular:", P), Spacer(1, 4),
 tabla([["Estación", "Tasa de llegada (pzs/min)", "Tiempo medio (min)", "Carga ofrecida", "Utilización simulada", "Cola máx."],
  ["Acondicionado 1", "0,500", "4,33", "217 %", f"{e['acond1'].utilizacion()*100:.1f} %", e["acond1"].q_max],
  ["Acondicionado 2", "0,429", "4,67", "200 %", f"{e['acond2'].utilizacion()*100:.1f} %", e["acond2"].q_max],
  ["Lotificado", "0,929 (si pasara todo)", "≈1,84 (mezcla)", "≈171 %", f"{e['lotif'].utilizacion()*100:.1f} %", e["lotif"].q_max],
  ["Reproceso", "5 % del lotificado", "5,00", "≈23 %", f"{e['reproc'].utilizacion()*100:.1f} %", e["reproc"].q_max]],
  [3.2*cm, 3.2*cm, 2.6*cm, 2.3*cm, 2.8*cm, 1.9*cm]), Spacer(1, 8),
 Paragraph(f"<b>Cuello de botella principal: Acondicionado 1.</b> Recibe una pieza cada 2 min pero tarda 4,33 min en promedio por pieza: su capacidad es ~0,23 pzs/min frente a 0,50 que llegan. "
  f"Trabajó al {e['acond1'].utilizacion()*100:.0f} % y acumuló una cola de hasta {e['acond1'].q_max} piezas (media {e['acond1'].cola_media():.0f}), con una espera media de {e['acond1'].espera_total/e['acond1'].salidas_iniciadas:.0f} min.", P), Spacer(1, 4),
 Paragraph(f"<b>Cuello de botella secundario: Acondicionado 2.</b> Llegan 0,43 pzs/min y la estación atiende 0,21 pzs/min. Utilización de {e['acond2'].utilizacion()*100:.0f} % y cola máxima de {e['acond2'].q_max} piezas.", P), Spacer(1, 4),
 Paragraph(f"<b>Lotificado no es el cuello hoy, pero lo será al corregir los anteriores.</b> Hoy recibe solo lo que los acondicionados logran liberar (~0,43 pzs/min) y trabaja al {e['lotif'].utilizacion()*100:.0f} %. "
  "Si se duplica la capacidad aguas arriba, su carga ofrecida (~171 %) lo convierte en el siguiente limitante: la lognormal del Producto B (2,83 min) pesa mucho en él. "
  "Reproceso queda muy holgado.", P), Spacer(1, 8),
 Paragraph("<b>Tiempos de fabricación (piezas terminadas en el turno).</b>", P), Spacer(1, 3),
 tabla([["Indicador", "Producto A", "Producto B", "Todos"],
  ["Piezas terminadas (almacén + basura)", base["out"]["almacen_A"] + base["out"]["basura_A"], base["out"]["almacen_B"] + base["out"]["basura_B"], base["out"]["almacen"] + base["out"]["basura"]],
  ["Tiempo medio en sistema (réplica 1)", f"{ciclo(base,'A'):.1f} min", f"{ciclo(base,'B'):.1f} min", f"{ciclo(base):.1f} min"],
  [f"Tiempo medio en sistema ({NREP} réplicas)", f"{m(reps['Base (1-1-1-1)'], lambda r: ciclo(r,'A')):.1f} min", f"{m(reps['Base (1-1-1-1)'], lambda r: ciclo(r,'B')):.1f} min", f"{m(reps['Base (1-1-1-1)'], ciclo):.1f} min"],
  ["Tiempo de proceso puro (sin esperas)", "≈ 5,3 min", "≈ 7,5 min", "-"]], [6.3*cm, 3*cm, 3*cm, 3*cm]),
 Paragraph("Estos tiempos solo cuentan piezas que ya salieron; las que siguen atrapadas en las colas al minuto 480 no aparecen, por lo que el tiempo de fabricación real es aún mayor que el mostrado. "
  f"Al cierre quedan {sum(base['wip'].values())} piezas sin terminar. El tiempo de proceso puro (~5 a 8 min) es una fracción pequeña del tiempo en sistema: casi todo es espera en cola.", SM),
 PageBreak()]
# 4
o = base["out"]
story += [Paragraph("4. Piezas enviadas al almacén y al cesto de basura", H1),
 tabla([["Destino", "Producto A", "Producto B", "Total"],
  ["Almacén de clientes (aprobadas en lotificado)", "", "", o["almacen_lotif"]],
  ["Almacén de clientes (aprobadas tras reproceso)", "", "", o["almacen_reproc"]],
  ["<b>Total almacén</b>", o["almacen_A"], o["almacen_B"], o["almacen"]],
  ["<b>Cesto de basura</b>", o["basura_A"], o["basura_B"], o["basura"]]], [8*cm, 2.6*cm, 2.6*cm, 2.6*cm]),
 Spacer(1, 8),
 Paragraph(f"En la réplica 1 llegaron al almacén <b>{o['almacen']}</b> piezas y al cesto de basura <b>{o['basura']}</b>. "
  f"Promediando {NREP} réplicas: <b>{m(reps['Base (1-1-1-1)'], lambda r: r['out']['almacen']):.0f} ± {ic(reps['Base (1-1-1-1)'], lambda r: r['out']['almacen']):.0f}</b> al almacén y "
  f"<b>{m(reps['Base (1-1-1-1)'], lambda r: r['out']['basura']):.1f} ± {ic(reps['Base (1-1-1-1)'], lambda r: r['out']['basura']):.1f}</b> a la basura (IC 95 %). "
  "La merma es pequeña (~2 % de lo procesado) porque solo el 5 % pasa por reproceso y el 40 % de ese grupo se descarta (5 % × 40 % = 2 %). "
  f"El verdadero problema no es la calidad, sino que se crearon {s['A'] + s['B']} piezas y solo {o['almacen'] + o['basura']} terminaron.", P),
 Spacer(1, 10)]
# 5 dashboard
story += [PageBreak(), Paragraph("5. Dashboard de resultados", H1)]
def img(n): return Image(f"{IMG}/g{n}.png", width=8.6*cm, height=5.3*cm)
story += [Table([[img(1), img(2)], [img(3), img(4)], [img(5), img(6)]], colWidths=[9*cm, 9*cm]), Spacer(1, 6),
 Paragraph("<b>Análisis.</b> (1) Los dos acondicionados están saturados (>97 %) mientras reproceso casi no se usa: el flujo está desbalanceado. "
  "(2) La cola de Acondicionado 1 crece de forma casi lineal durante todo el turno y nunca se estabiliza, señal clásica de sistema inestable (llegadas > capacidad); Acondicionado 2 hace lo mismo con menor pendiente y lotificado se mantiene cerca de cero. "
  f"(3) El destino final es ~{o['almacen_A']/(o['almacen_A']+o['almacen_B'])*100:.0f} % A y ~{o['almacen_B']/(o['almacen_A']+o['almacen_B'])*100:.0f} % B en el almacén, y la basura es marginal. "
  "(4) Los tiempos en sistema se dispersan hacia valores altos (cientos de minutos), consecuencia directa de esperar en las colas de acondicionado. "
  "(5) y (6) Comparan el caso base con las propuestas de la sección 6: la capacidad extra duplica la producción y el WIP casi desaparece.", P), PageBreak()]
# 6
def fila(k, nombre):
    r = reps[k]
    return [nombre, f"{m(r, lambda x: x['out']['almacen']):.0f} ± {ic(r, lambda x: x['out']['almacen']):.0f}",
            f"{m(r, lambda x: x['out']['basura']):.1f}", f"{m(r, ciclo):.1f}", f"{m(r, lambda x: sum(x['wip'].values())):.0f}",
            f"{m(r, lambda x: x['est']['acond1'].utilizacion())*100:.0f} / {m(r, lambda x: x['est']['acond2'].utilizacion())*100:.0f} / {m(r, lambda x: x['est']['lotif'].utilizacion())*100:.0f}"]
story += [Paragraph("6. Propuesta de mejora", H1),
 Paragraph("Para cada cuello se calculó cuántas estaciones paralelas hacen falta (utilización objetivo ≤ 75-85 %) y se simuló el resultado (30 réplicas por escenario).", P), Spacer(1, 4),
 tabla([["Cuello", "Carga", "Acción propuesta"],
  ["Acondicionado 1", "217 %", "Tres puestos en paralelo (utilización ≈ 72 %) o reducir el tiempo medio con estandarizar limpieza/etiquetado y pre-etiquetas impresas"],
  ["Acondicionado 2", "200 %", "Tres puestos en paralelo (utilización ≈ 67 %); mismas acciones de método"],
  ["Lotificado (cuello latente)", "≈ 171 % al liberar lo anterior", "Segundo puesto/impresora (utilización ≈ 82 %); revisar por qué el producto B tarda 2,83 min vs 1 min de A"],
  ["Calidad / reproceso", "≈ 23 %", "Sin cambio de capacidad; atacar la causa del 5 % de defectos de impresión (mantenimiento de la impresora, verificación del primer lote)"]],
  [3.3*cm, 3.3*cm, 9.4*cm]), Spacer(1, 8),
 tabla([["Escenario (aco1-aco2-lot)", "Piezas al almacén", "Basura", "Tiempo medio en sistema (min)", "WIP final", "Util. % (A1/A2/Lot)"],
  fila("Base (1-1-1-1)", "Base 1-1-1"), fila("Mejora 1 (3 acond. por línea)", "Mejora 1: 3-3-1"), fila("Mejora 2 (3-3-2 + reproceso 1)", "Mejora 2: 3-3-2")],
  [3.8*cm, 2.7*cm, 1.5*cm, 3.2*cm, 1.8*cm, 3*cm]), Spacer(1, 8),
 Paragraph("<b>Lectura.</b> Agregar solo capacidad de acondicionado (Mejora 1) sube la producción pero traslada el cuello a Lotificado (utilización ≈ 98 %, WIP todavía alto), lo que confirma que un cuello corregido deja ver el siguiente. "
  "Con la Mejora 2 los tres procesos quedan por debajo de ~82 %, la cola desaparece y el tiempo medio en sistema baja a unos 14 min, cerca del tiempo de proceso puro. "
  "La producción queda limitada por la demanda de llegadas (~0,93 pzs/min), no por la capacidad. "
  "Como las tres estaciones extra implican inversión, una alternativa de menor costo es combinar un puesto adicional por línea con reducción de tiempos de método; debe evaluarse con el costo real de cada operario o equipo.", P), PageBreak()]
# 7
story += [Paragraph("7. Conclusiones", H1)]
for t in [
 f"El sistema, tal como está, no es capaz de absorber la demanda: en 480 min entraron {s['A'] + s['B']} piezas y solo {o['almacen'] + o['basura']} terminaron; el resto quedó en colas.",
 "Los cuellos de botella son Acondicionado 1 (carga 217 %) y Acondicionado 2 (carga 200 %): la causa es que su tiempo medio de proceso es más del doble del intervalo entre llegadas.",
 f"Se enviaron {o['almacen']} piezas al almacén y {o['basura']} al cesto de basura en la réplica 1 (promedio de {NREP} réplicas: {m(reps['Base (1-1-1-1)'], lambda r: r['out']['almacen']):.0f} y {m(reps['Base (1-1-1-1)'], lambda r: r['out']['basura']):.1f}); la pérdida por calidad es de ~2 % y no es el problema principal.",
 "El tiempo de fabricación real (>100 min) es muy superior al tiempo de proceso puro (5 a 8 min) por las esperas; es la métrica que más mejora al quitar los cuellos.",
 "Con 3 puestos por acondicionado y 2 de lotificado la producción pasa de ~205 a ~420 piezas por turno, y el tiempo en sistema de ~130 a ~14 min. Resolver un cuello sin mirar el siguiente (Mejora 1) deja el problema en Lotificado.",
 "Limitaciones: colas infinitas, un solo turno sin período de calentamiento, y un supuesto sobre la parametrización de la lognormal; deben verificarse en el modelo FlexSim propio."]:
    story += [Paragraph("• " + t, P), Spacer(1, 3)]
story += [Spacer(1, 10), Paragraph("Anexo. Guía para construir el modelo en FlexSim", H1)]
for t in ["<b>Objetos:</b> Source A, Source B, Separator (o Processor con Output Split) para B, Processor Acondicionado 1, Processor Acondicionado 2, Processor Lotificado, Processor Reproceso, Sink Almacén, Sink Basura. Cada Processor tiene su Queue de entrada.",
 "<b>Source A:</b> Inter-arrival Time = exponential(0, 2, 0). <b>Source B:</b> exponential(0, 7, 0), con Arrival Style por lotes y cantidad 3 (o Separator con Split Quantity 3 / Unpack). Asigne Item Type 1 a A y 2 a B.",
 "<b>Acondicionado 1:</b> Process Time = triangular(1, 8, 4, 0) (en FlexSim el orden es mín, máx, moda). <b>Acondicionado 2:</b> triangular(2, 8, 4, 0).",
 "<b>Lotificado:</b> Process Time = getitemtype(item)==1 ? normal(1, 0.2, 0) : lognormal2(0, 2.5, 0.5, 0). <b>Reproceso:</b> 5. Conéctelo desde Lotificado con Send To Port por porcentaje: 95 % al almacén, 5 % a Reproceso. Desde Reproceso: 60 % al almacén, 40 % a basura.",
 "<b>Ejecución:</b> Run Time = 480 min (fije el modelo en minutos). Con Statistics Collectors agregue gráficos de utilización, cola y throughput, y use Dashboard → Create Dashboard para los 4+ gráficos. Los paneles de la sección 2 se obtienen con doble clic en cada objeto (pestañas Properties y Statistics)."]:
    story += [Paragraph("• " + t, P), Spacer(1, 3)]

def pie(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#777777"))
    c.drawString(2*cm, 1.2*cm, "Simulación de procesos de producción con FlexSim"); c.drawRightString(letter[0] - 2*cm, 1.2*cm, f"Pág. {d.page}"); c.restoreState()

doc = SimpleDocTemplate(os.path.join(D, "Informe_Simulacion_FlexSim.pdf"), pagesize=letter, leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=1.8*cm, bottomMargin=2*cm, title="Simulación de procesos con FlexSim")
doc.build(story, onLaterPages=pie)
print("OK")
