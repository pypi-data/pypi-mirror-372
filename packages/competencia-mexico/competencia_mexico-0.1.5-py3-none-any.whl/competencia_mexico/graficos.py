import math
import pandas as pd
import matplotlib.pyplot as plt

# (Opcional) helper si empaquetas el CSV dentro del paquete
def _cargar_csv_empaquetado(nombre_empaquetado: str) -> pd.DataFrame:
    """
    Carga un CSV incluido en el paquete. Ajusta el paquete/ruta según tu estructura.
    """
    try:
        from importlib.resources import files
        # Cambia 'tu_paquete' por el nombre real del paquete donde va el CSV
        path = files("tu_paquete").joinpath(nombre_empaquetado)
        return pd.read_csv(path)
    except Exception as e:
        raise FileNotFoundError(
            f"No pude cargar '{nombre_empaquetado}' desde el paquete. "
            f"Asegúrate de declararlo en package_data / MANIFEST.in. Error: {e}"
        )

def graficar_y_resumir_asuntos_interactiva(
    ruta_csv: str | None = None,
    df: pd.DataFrame | None = None,
    nombre_empaquetado: str = "estadisticas_final.csv",
):
    # 1) Fuente de datos (precedencia: df -> ruta_csv -> empaquetado)
    if df is not None:
        base = df.copy()
    elif ruta_csv is not None:
        base = pd.read_csv(ruta_csv)
    else:
        base = _cargar_csv_empaquetado(nombre_empaquetado)

    # 2) Validar columnas necesarias
    requeridas = ['FechaResolucion', 'Rubro', 'Decision']
    faltantes = [c for c in requeridas if c not in base.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")

    # 3) Asegurar formato de fecha
    base = base.copy()
    base["FechaResolucion"] = pd.to_datetime(base["FechaResolucion"], errors="coerce")

    # 4) Opciones de rubro
    rubros_disponibles = (
        base["Rubro"].dropna().astype(str).str.upper().unique().tolist()
    )
    print("\n Graficador de asuntos")
    print("-------------------------")
    print("Rubros disponibles:", ', '.join(sorted(rubros_disponibles)))

    # 5) Inputs
    rubro = input("\n¿Qué rubro quieres graficar? (Ej. DE, IO, OPN): ").strip().upper()
    if rubro not in rubros_disponibles:
        raise ValueError(f"El rubro '{rubro}' no está en los datos.")

    desagregacion = input("¿Quieres agrupar por mes o por año? [mes/año]: ").strip().lower()
    desagregacion = desagregacion.replace("ñ", "n")  # permitir 'año'/'ano'
    if desagregacion not in ["mes", "ano"]:
        raise ValueError("Debes escribir 'mes' o 'año' (también se acepta 'ano').")

    por_decision = input("¿Quieres desglosar por tipo de decisión? [s/n]: ").strip().lower()
    if por_decision not in ["s", "n"]:
        raise ValueError("Responde 's' para sí o 'n' para no.")
    por_decision = (por_decision == "s")

    # 6) Filtrar por rubro y fechas válidas (usa .copy() para evitar SettingWithCopy)
    base = base[base["Rubro"].astype(str).str.upper() == rubro].dropna(subset=["FechaResolucion"]).copy()

    # 7) Crear columna Periodo (como Period para ordenar bien)
    if desagregacion == "mes":
        base["Periodo"] = base["FechaResolucion"].dt.to_period("M")
    else:
        base["Periodo"] = base["FechaResolucion"].dt.to_period("Y")

    # 8) Agrupar y graficar
    if por_decision:
        resumen = base.groupby(["Periodo", "Decision"]).size().unstack(fill_value=0).sort_index()
        ax = resumen.plot(kind="bar", stacked=True, figsize=(12, 6))
        plt.title(f"Asuntos por {'mes' if desagregacion=='mes' else 'año'} (Rubro '{rubro}') por decisión")
    else:
        resumen = base.groupby("Periodo").size().sort_index()
        ax = resumen.plot(kind="bar", figsize=(10, 5))
        plt.title(f"Asuntos por {'mes' if desagregacion=='mes' else 'año'} (Rubro '{rubro}')")

    # 9) Ajustes estéticos
    plt.xlabel("Periodo")
    plt.ylabel("Número de asuntos")

    # “Adelgazar” etiquetas de eje X de forma dinámica
    xticks = ax.get_xticklabels()
    if len(xticks) > 15:
        step = math.ceil(len(xticks) / 15)
        for i, lab in enumerate(xticks):
            lab.set_visible(i % step == 0)

    ax.set_xticklabels([str(x.get_text()) for x in xticks], rotation=45)
    plt.tight_layout()
    plt.show()

    # 10) Tabla resumen robusta
    if por_decision:
        resumen_final = resumen.reset_index()
    else:
        # Series -> DataFrame con nombre predecible
        resumen_final = resumen.to_frame("Total").reset_index()
        # Si quieres el Periodo como string “YYYY-MM” / “YYYY”
        resumen_final["Periodo"] = resumen_final["Periodo"].astype(str)

    try:
        from IPython.display import display
        print("\n Tabla resumen:")
        display(resumen_final)
    except Exception:
        print("\n Tabla resumen:")
        print(resumen_final.head(20).to_string(index=False))

    return resumen_final
