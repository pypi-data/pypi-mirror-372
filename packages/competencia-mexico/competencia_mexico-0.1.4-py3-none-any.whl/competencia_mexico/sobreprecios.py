import matplotlib.pyplot as plt
import numpy as np

def perdida_colusion(precio_competencia, precio_colusion, cantidad_competencia, elasticidad):
    """
    Calcula y grafica la pérdida de bienestar bajo colusión,
    ajustando la pendiente de la demanda a la elasticidad proporcionada.
    
    Parámetros:
    - precio_competencia: Precio en competencia (P0)
    - precio_colusion: Precio en colusión (P1)
    - cantidad_competencia: Cantidad demandada a P0 (Q0)
    - elasticidad: Elasticidad-precio de la demanda (negativa)

    Retorna:
    - area_A: Transferencia (P1 - P0) * Q1
    - area_B: Pérdida irrecuperable 0.5 * (P1 - P0) * (Q0 - Q1)
    """
    P0 = precio_competencia
    P1 = precio_colusion
    Q0 = cantidad_competencia
    e = elasticidad

    # Calcular Q1 usando fórmula de elasticidad
    Q1 = Q0 * (1 + e * (P1 - P0) / P0)
    Q1 = max(Q1, 0)  # no negativa

    # Área A: transferencia del consumidor al productor
    area_A = (P1 - P0) * Q1

    # Área B: pérdida irrecuperable
    area_B = 0.5 * (P1 - P0) * (Q0 - Q1)

    # Calculamos pendiente de la demanda lineal usando elasticidad
    b = -e * Q0 / P0  # pendiente
    a = Q0 + b * P0   # intersección con eje cantidad (cuando P = 0)

    # Generar puntos de demanda
    precios = np.linspace(0, P1 * 1.2, 200)
    cantidades = a - b * precios

    # Gráfica
    plt.figure(figsize=(8, 6))

    # Demanda
    plt.plot(cantidades, precios, label='Demanda (D)', color='black')

    # Líneas auxiliares
    plt.vlines(Q0, 0, P0, linestyles='dashed', colors='gray')
    plt.vlines(Q1, 0, P1, linestyles='dashed', colors='gray')
    plt.hlines(P0, 0, Q0, linestyles='dotted', colors='gray')
    plt.hlines(P1, 0, Q1, linestyles='dotted', colors='gray')

    # Área A
    plt.fill_between([0, Q1], P0, P1, color='orange', alpha=0.6, label='Área A (Transferencia al productor)')

    # Área B como triángulo
    plt.fill([Q1, Q1, Q0], [P1, P0, P0], color='red', alpha=0.5, label='Área B (Pérdida irrecuperable de eficiencia)')

    plt.title('Pérdida del consumidor por colusión')
    plt.xlabel('Cantidad')
    plt.ylabel('Precio')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend()
    #plt.grid(True)
    plt.show()

    print(f"Área A (Transferencia al productor): ${area_A:,.2f}")
    print(f"Área B (Pérdida irrecuperable de eficiencia): ${area_B:,.2f}")

    return area_A, area_B



def calcular_sobreprecio(df, col_base, col_nueva, nombre_columna_resultado="Sobreprecio (%)"):
    """
    Calcula el sobreprecio porcentual entre dos columnas de precios en un DataFrame.

    Parámetros:
    - df: DataFrame que contiene las columnas de precios.
    - col_base: nombre de la columna con el precio original o base.
    - col_nueva: nombre de la columna con el nuevo precio.
    - nombre_columna_resultado: nombre para la columna resultante (opcional).

    Retorna:
    - nuevo DataFrame con columna adicional del sobreprecio porcentual.
    """
    import pandas as pd
    import numpy as np
    df_resultado = df.copy()
    df_resultado[nombre_columna_resultado] = np.where(
        (df_resultado[col_base].notnull()) & (df_resultado[col_base] != 0),
        ((df_resultado[col_nueva] - df_resultado[col_base]) / df_resultado[col_base]) * 100,
        np.nan
    )
    return df_resultado


def aumentar_precios(df, columnas_precios, porcentaje_aumento, graficar=True):
    """
    Aumenta los precios en las columnas indicadas por un porcentaje dado y grafica el cambio.

    Parámetros:
    - df: DataFrame original.
    - columnas_precios: lista de nombres de columnas a modificar.
    - porcentaje_aumento: número decimal. Por ejemplo, 0.05 para 5% de aumento.
    - graficar: si True, muestra gráficos comparando precios antes y después.

    Retorna:
    - nuevo DataFrame con los precios actualizados.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    df_nuevo = df.copy()

    for col in columnas_precios:
        if col in df_nuevo.columns:
            # Guardar precios originales
            df_nuevo[f"{col}_original"] = df_nuevo[col]
            # Aplicar aumento
            df_nuevo[col] = df_nuevo[col].apply(
                lambda x: x * (1 + porcentaje_aumento) if pd.notnull(x) else x
            )

            # Graficar si se solicita
            if graficar:
                plt.figure(figsize=(10, 5))
                plt.plot(df.index, df[col], label="Precio original", marker='o')
                plt.plot(df.index, df_nuevo[col], label="Precio aumentado", marker='x')
                plt.title(f'Comparación de precios: {col}')
                plt.xlabel("Periodos o productos")
                plt.ylabel("Precio")
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                plt.show()

    return df_nuevo