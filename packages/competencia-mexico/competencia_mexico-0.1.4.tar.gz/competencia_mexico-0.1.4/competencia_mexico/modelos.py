from typing import Any, Dict, List, Tuple, Optional, Literal
import math, json

def analizar_mercado(
    modelo: Literal["monopolio", "cournot", "bertrand", "stackelberg", "opciones"],
    demanda: Literal["lineal", "cobb-douglas"] = "lineal",
    *,
    # Demanda lineal: P = a - b Q
    a: Optional[float] = None,
    b: Optional[float] = None,
    # Demanda isoelástica (“Cobb‑Douglas”): P = k * Q^(-1/epsilon), epsilon>1
    k: Optional[float] = None,
    epsilon: Optional[float] = None,
    # Costos
    c: float = 0.0,       # costo marginal
    f: float = 0.0,       # costo fijo por firma
    # Estructura
    n_firmas: int = 1,    # Cournot/Bertrand
    n_seguidores: int = 1, # Stackelberg: 1 líder + n_seguidores
    # Salida
    salida: Literal["filas", "anchas", "objeto"] = "filas",
    imprimir: bool = False,     # imprime tabla legible en consola
) -> Any:
    """
    Resuelve y formatea equilibrios IO en una sola función.

    Parámetros clave:
    - modelo: "monopolio" | "cournot" | "bertrand" | "stackelberg" | "opciones"
    - demanda: "lineal" | "cobb-douglas" (isoelástica)
    - a, b: para demanda lineal (P = a - bQ), b>0
    - k, epsilon: para demanda isoelástica (P = k * Q^(-1/epsilon)), k>0, epsilon>1
    - c, f: costo marginal y costo fijo por firma
    - n_firmas: # de firmas (Cournot/Bertrand)
    - n_seguidores: # seguidores (Stackelberg; hay 1 líder)
    - salida: "filas" (tabla 2 columnas) | "anchas" (1 fila muchas columnas) | "objeto" (dict)
    - imprimir: si True, muestra tabla legible en consola

    Devuelve:
    - Si salida="filas": DataFrame (si hay pandas) o lista de (campo, valor)
    - Si salida="anchas": DataFrame (si hay pandas) o dict
    - Si salida="objeto": dict con todos los campos
    - Si modelo="opciones": dict con catálogo de opciones/parámetros
    """
    # ====== Catálogo de opciones ======
    def _catalogo() -> Dict[str, Any]:
        return {
            "modelos_validos": ["monopolio", "cournot", "bertrand", "stackelberg"],
            "demandas_validas": ["lineal", "cobb-douglas"],
            "parametros_generales": {
                "c": "costo marginal constante (float, >=0)",
                "f": "costo fijo por firma (float, >=0, opcional)",
            },
            "parametros_por_demanda": {
                "lineal": {
                    "a": "intercepto demanda inversa (P = a - bQ)",
                    "b": "pendiente positiva (>0) de demanda inversa",
                },
                "cobb-douglas": {
                    "k": "escala en P(Q) = k * Q^(-1/epsilon) (k>0)",
                    "epsilon": "elasticidad-precio (>1)",
                },
            },
            "parametros_por_modelo": {
                "monopolio": {"n_firmas": "ignorado", "n_seguidores": "ignorado"},
                "cournot": {"n_firmas": "int >= 2"},
                "bertrand": {"n_firmas": "int >= 2; bienes homogéneos, costos idénticos"},
                "stackelberg": {"n_seguidores": "int >= 1 (1 líder + n seguidores)"},
            },
            "notas": [
                "“Cobb‑Douglas” se implementa como demanda isoelástica: P(Q)=k·Q^(-1/epsilon).",
                "En Bertrand (bienes homogéneos, costos idénticos) el equilibrio clásico es p*=c.",
                "Cournot isoelástico usa Lerner: (P-c)/P = 1/(N·epsilon).",
                "Stackelberg lineal usa fórmulas cerradas; isoelástica se resuelve numéricamente.",
            ],
        }

    if modelo.lower() == "opciones":
        cat = _catalogo()
        if imprimir:
            _imprimir_tabla([("Campo", "Valor")]+[(k, ", ".join(v) if isinstance(v, list) else v)
                              for k,v in {
                                  "Modelos": cat["modelos_validos"],
                                  "Demandas": cat["demandas_validas"],
                                  "Notas": "; ".join(cat["notas"])
                              }.items()])
        return cat

    # ====== Utilidades de demanda ======
    def p_lineal(a: float, b: float, Q: float) -> float:
        return max(0.0, a - b * Q)

    def p_iso(k: float, eps: float, Q: float) -> float:
        if Q <= 0:
            return float("inf")
        return k * (Q ** (-1.0 / eps))

    # ====== Validaciones ======
    modelo = modelo.lower()
    demanda = demanda.lower()
    if demanda == "lineal":
        if a is None or b is None:
            raise ValueError("Demanda lineal: especifica a y b.")
        if b <= 0:
            raise ValueError("En demanda lineal, b debe ser > 0.")
    elif demanda == "cobb-douglas":
        if k is None or epsilon is None:
            raise ValueError("Demanda Cobb‑Douglas: especifica k y epsilon.")
        if k <= 0 or epsilon <= 1:
            raise ValueError("Requiere k>0 y epsilon>1.")
    else:
        raise ValueError("Demanda no reconocida.")

    if c < 0 or f < 0:
        raise ValueError("c y f no pueden ser negativos.")
    if modelo in ("cournot", "bertrand") and n_firmas < 2:
        raise ValueError("Para Cournot/Bertrand, n_firmas ≥ 2.")
    if modelo == "stackelberg" and n_seguidores < 1:
        raise ValueError("Stackelberg requiere al menos 1 seguidor.")

    # ====== Resolver por caso ======
    cantidades: List[float] = []
    precio: float = float("nan")

    if modelo == "monopolio":
        if demanda == "lineal":
            if a <= c:
                Q = 0.0
            else:
                Q = (a - c) / (2 * b)
            precio = p_lineal(a, b, Q)
            cantidades = [Q]
        else:
            P_star = (epsilon / (epsilon - 1.0)) * c if c > 0 else 1e-9
            Q = (k / P_star) ** epsilon if P_star > 0 else float("inf")
            precio = p_iso(k, epsilon, Q)
            cantidades = [Q]

    elif modelo == "cournot":
        N = n_firmas
        if demanda == "lineal":
            if a <= c:
                Q = 0.0
                precio = p_lineal(a, b, Q)
                cantidades = [0.0] * N
            else:
                q_i = (a - c) / (b * (N + 1))
                cantidades = [q_i] * N
                Q = N * q_i
                precio = p_lineal(a, b, Q)
        else:
            if N * epsilon <= 1:
                raise ValueError("Cournot isoelástico requiere N*epsilon > 1.")
            P_star = (N * epsilon) / (N * epsilon - 1.0) * c if c > 0 else 1e-9
            Q = (k / P_star) ** epsilon if P_star > 0 else float("inf")
            precio = p_iso(k, epsilon, Q)
            cantidades = [Q / N] * N

    elif modelo == "bertrand":
        N = n_firmas
        precio = c
        if demanda == "lineal":
            Q = max(0.0, (a - precio) / b)
        else:
            Q = (k / precio) ** epsilon if precio > 0 else float("inf")
        qi = Q / N
        cantidades = [qi] * N

    elif modelo == "stackelberg":
        n = n_seguidores
        if demanda == "lineal":
            if a <= c:
                qL = qF = 0.0
            else:
                qL = (a - c) / (2 * b)
                qF = (a - c) / (2 * b * (n + 1))
            cantidades = [qL] + [qF] * n
            Q = sum(cantidades)
            precio = p_lineal(a, b, Q)
        else:
            def P(Q): return p_iso(k, epsilon, Q)
            def seguidores_br(qL: float) -> float:
                # se resuelve (P(Q)-c) - qF*P(Q)/(epsilon*Q) = 0 por bisección, revisar si podemos hacerlo en forma cerrada o disminuyendo n
                qlow, qhigh = 0.0, max(1.0, (k / max(c, 1e-9)) ** epsilon)
                for _ in range(80):
                    qm = 0.5 * (qlow + qhigh)
                    Qm = qL + n * qm
                    if Qm <= 0:
                        qlow = qm
                        continue
                    Pm = P(Qm)
                    g = (Pm - c) - (qm * Pm) / (epsilon * Qm)
                    if g > 0:
                        qlow = qm
                    else:
                        qhigh = qm
                return 0.5 * (qlow + qhigh)

            def pi_lider(qL: float) -> float:
                qF = seguidores_br(qL)
                Q = qL + n * qF
                return max(0.0, (P(Q) - c)) * qL

            Qcap = (k / max(c, 1e-9)) ** epsilon
            candidatos = [(pi_lider(0.0), 0.0)]
            candidatos += [(pi_lider(Qcap * t / 40), Qcap * t / 40) for t in range(1, 41)]
            qL0 = max(candidatos)[1]
            paso = max(1e-6, qL0 * 0.2)
            mejor_qL, mejor_pi = qL0, pi_lider(qL0)
            for _ in range(40):
                for q_try in (max(0.0, mejor_qL - paso), mejor_qL + paso):
                    pi_try = pi_lider(q_try)
                    if pi_try > mejor_pi + 1e-12:
                        mejor_qL, mejor_pi = q_try, pi_try
                paso *= 0.5
            qL_star = max(0.0, mejor_qL)
            qF_star = seguidores_br(qL_star)
            cantidades = [qL_star] + [qF_star] * n
            Q = sum(cantidades)
            precio = P(Q)
    else:
        raise ValueError("Modelo no reconocido.")

    # ====== Ganancias por firma ======
    Q_total = sum(cantidades)
    p_equil = p_lineal(a, b, Q_total) if demanda == "lineal" else p_iso(k, epsilon, Q_total)
    ganancias = [(max(0.0, p_equil - c) * q) - f for q in cantidades]

    # ====== Objeto base ======
    objeto = {
        "modelo": modelo,
        "demanda": demanda,
        "precio": p_equil,
        "cantidad_total": Q_total,
        "cantidades_por_empresa": cantidades,
        "ganancias_por_empresa": ganancias,
        "parametros": {
            "a": a, "b": b, "k": k, "epsilon": epsilon,
            "c": c, "f": f, "n_firmas": n_firmas, "n_seguidores": n_seguidores
        }
    }

    # ====== Formateadores ======
    def a_filas(obj: Dict[str, Any]) -> List[Tuple[str, Any]]:
        filas: List[Tuple[str, Any]] = [
            ("Modelo", obj["modelo"]),
            ("Demanda", obj["demanda"]),
            ("Precio de equilibrio", round(obj["precio"], 6)),
            ("Cantidad total", round(obj["cantidad_total"], 6)),
        ]
        for i, q in enumerate(obj["cantidades_por_empresa"], 1):
            filas.append((f"Cantidad firma {i}", round(q, 6)))
        for i, pi in enumerate(obj["ganancias_por_empresa"], 1):
            filas.append((f"Ganancia firma {i}", round(pi, 6)))
        filas.append(("—", "—"))
        filas.append(("Parámetros utilizados", ""))
        for key in ["a","b","k","epsilon","c","f","n_firmas","n_seguidores"]:
            filas.append((key, obj["parametros"].get(key)))
        return filas

    def a_dataframe(filas_o_base, orient: str):
        try:
            import pandas as pd
        except Exception:
            return filas_o_base
        if orient == "filas":
            return pd.DataFrame(filas_o_base, columns=["Campo", "Valor"])
        elif orient == "anchas":
            base = {
                "modelo": objeto["modelo"],
                "demanda": objeto["demanda"],
                "precio": objeto["precio"],
                "cantidad_total": objeto["cantidad_total"],
            }
            for i, q in enumerate(objeto["cantidades_por_empresa"], 1):
                base[f"q_{i}"] = q
            for i, pi in enumerate(objeto["ganancias_por_empresa"], 1):
                base[f"pi_{i}"] = pi
            for kparam, vparam in objeto["parametros"].items():
                base[f"param_{kparam}"] = vparam
            return pd.DataFrame([base])
        else:
            raise ValueError("orient debe ser 'filas' o 'anchas'.")

    def _imprimir_tabla(filas: List[Tuple[str, Any]], ancho: int = 36) -> None:
        sep = "-" * (ancho * 2 + 5)
        print(sep)
        print(f"{'Campo'.ljust(ancho)} | Valor")
        print(sep)
        for campo, valor in filas:
            val = json.dumps(valor) if isinstance(valor, (dict, list)) else str(valor)
            print(f"{campo.ljust(ancho)} | {val}")
        print(sep)

    # ====== Selección de salida ======
    if salida == "objeto":
        if imprimir:
            _imprimir_tabla(a_filas(objeto))
        return objeto

    elif salida == "filas":
        filas = a_filas(objeto)
        if imprimir:
            _imprimir_tabla(filas)
        return a_dataframe(filas, "filas")

    elif salida == "anchas":
        df_o_dict = a_dataframe(None, "anchas")
        if imprimir:
            _imprimir_tabla(a_filas(objeto))
        return df_o_dict

    else:
        raise ValueError("salida debe ser 'filas', 'anchas' o 'objeto'.")
