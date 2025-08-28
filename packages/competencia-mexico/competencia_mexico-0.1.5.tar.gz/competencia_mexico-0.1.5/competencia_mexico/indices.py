def variacion_dominancia_interactiva():
    import pandas as pd

    print("Cálculo de la variación del índice de dominancia por fusión de empresas\n")

    # Selección de modo de ingreso de datos
    modo = input("¿Quieres usar un DataFrame desde archivo CSV (d) o ingresar manualmente (m)? [d/m]: ").strip().lower()
    if modo not in ["d", "m"]:
        raise ValueError("Opción inválida. Escribe 'd' para DataFrame o 'm' para manual.")

    # Tipo de dato
    tipo_dato = input("¿Qué tipo de dato vas a ingresar? Escribe 'porcentaje' o 'valores': ").strip().lower()
    if tipo_dato not in ["porcentaje", "valores"]:
        raise ValueError("tipo_dato debe ser 'porcentaje' o 'valores'.")

    # Cargar o ingresar datos
    if modo == "d":
        ruta = input("Ruta del archivo CSV con columnas 'empresa' y 'participacion': ").strip()
        df = pd.read_csv(ruta)
        if not {'empresa', 'participacion'}.issubset(df.columns):
            raise ValueError("El archivo debe contener las columnas 'empresa' y 'participacion'.")
    else:
        n = int(input("¿Cuántas empresas quieres ingresar? "))
        empresas = []
        participaciones = []
        for i in range(n):
            nombre = input(f"Nombre de la empresa {i+1}: ").strip()
            valor = float(input(f"{'Participación (%)' if tipo_dato == 'porcentaje' else 'Valor absoluto'} de '{nombre}': "))
            empresas.append(nombre)
            participaciones.append(valor)

        df = pd.DataFrame({
            "empresa": empresas,
            "participacion": participaciones
        })

    print("\nEmpresas disponibles:", ', '.join(df["empresa"]))
    empresa1 = input("Nombre de la primera empresa que se fusionará: ").strip()
    empresa2 = input("Nombre de la segunda empresa que se fusionará: ").strip()

    if empresa1 not in df["empresa"].values or empresa2 not in df["empresa"].values:
        raise ValueError("Una o ambas empresas no están en el DataFrame.")

    # Normalización
    participaciones = df["participacion"].copy()

    if tipo_dato == "porcentaje":
        if participaciones.sum() > 100:
            raise ValueError("La suma de las participaciones supera el 100%. Verifica tus datos.")
        participaciones = participaciones / 100

    elif tipo_dato == "valores":
        total = participaciones.sum()
        if total == 0:
            raise ValueError("La suma de los valores es cero. No se puede calcular el índice de dominancia.")
        participaciones = participaciones / total

    df["participacion_normalizada"] = participaciones

    # Índice de dominancia antes de la fusión
    dominancia_antes = participaciones.max()

    # Fusión
    p1 = df.loc[df["empresa"] == empresa1, "participacion_normalizada"].values[0]
    p2 = df.loc[df["empresa"] == empresa2, "participacion_normalizada"].values[0]
    nueva_participacion = p1 + p2

    df_fusionada = df[~df["empresa"].isin([empresa1, empresa2])].copy()

    nueva_fila = pd.DataFrame({
        "empresa": [f"{empresa1}-{empresa2}"],
        "participacion_normalizada": [nueva_participacion]
    })

    df_fusionada = pd.concat([df_fusionada, nueva_fila], ignore_index=True)

    # Índice de dominancia después de la fusión
    dominancia_despues = df_fusionada["participacion_normalizada"].max()

    variacion = dominancia_despues - dominancia_antes

    # Mostrar resultado con estilo
    print("\n" + "-"*45)
    print("RESULTADO DE LA FUSIÓN (Índice de dominancia)".center(45))
    print("-"*45)
    print(f"{'Dominancia antes de la fusión:':<35}{round(dominancia_antes * 10000, 2):>8}")
    print(f"{'Dominancia después de la fusión:':<35}{round(dominancia_despues * 10000, 2):>8}")
    print(f"{'Variación del índice de dominancia:':<35}{round(variacion * 10000, 2):>8}")
    print("-"*45)

    return {
        "dominancia_antes": float(round(dominancia_antes * 10000, 2)),
        "dominancia_despues": float(round(dominancia_despues * 10000, 2)),
        "variacion_dominancia": float(round(variacion * 10000, 2))
    }

def variacion_ihh_interactiva():
    import pandas as pd

    print("Cálculo de la variación del IHH por fusión de empresas\n")

    # Selección de modo de ingreso de datos
    modo = input("¿Quieres usar un DataFrame desde archivo CSV (d) o ingresar manualmente (m)? [d/m]: ").strip().lower()
    if modo not in ["d", "m"]:
        raise ValueError("Opción inválida. Escribe 'd' para DataFrame o 'm' para manual.")

    # Tipo de dato
    tipo_dato = input("¿Qué tipo de dato vas a ingresar? Escribe 'porcentaje' o 'valores': ").strip().lower()
    if tipo_dato not in ["porcentaje", "valores"]:
        raise ValueError("tipo_dato debe ser 'porcentaje' o 'valores'.")

    # Cargar o ingresar datos
    if modo == "d":
        ruta = input("Ruta del archivo CSV con columnas 'empresa' y 'participacion': ").strip()
        df = pd.read_csv(ruta)
        if not {'empresa', 'participacion'}.issubset(df.columns):
            raise ValueError("El archivo debe contener las columnas 'empresa' y 'participacion'.")
    else:
        n = int(input("¿Cuántas empresas quieres ingresar? "))
        empresas = []
        participaciones = []
        for i in range(n):
            nombre = input(f"Nombre de la empresa {i+1}: ").strip()
            valor = float(input(f"{'Participación (%)' if tipo_dato == 'porcentaje' else 'Valor absoluto'} de '{nombre}': "))
            empresas.append(nombre)
            participaciones.append(valor)

        df = pd.DataFrame({
            "empresa": empresas,
            "participacion": participaciones
        })

    print("\nEmpresas disponibles:", ', '.join(df["empresa"]))
    empresa1 = input("Nombre de la primera empresa que se fusionará: ").strip()
    empresa2 = input("Nombre de la segunda empresa que se fusionará: ").strip()

    if empresa1 not in df["empresa"].values or empresa2 not in df["empresa"].values:
        raise ValueError("Una o ambas empresas no están en el DataFrame.")

    # Normalización
    participaciones = df["participacion"].copy()

    if tipo_dato == "porcentaje":
        if participaciones.sum() > 100:
            raise ValueError("La suma de las participaciones supera el 100%. Verifica tus datos.")
        participaciones = participaciones / 100

    elif tipo_dato == "valores":
        total = participaciones.sum()
        if total == 0:
            raise ValueError("La suma de los valores es cero. No se puede calcular el IHH.")
        participaciones = participaciones / total

    df["participacion_normalizada"] = participaciones

    # IHH antes de la fusión
    ihh_antes = (df["participacion_normalizada"] ** 2).sum()

    # Fusión
    p1 = df.loc[df["empresa"] == empresa1, "participacion_normalizada"].values[0]
    p2 = df.loc[df["empresa"] == empresa2, "participacion_normalizada"].values[0]
    nueva_participacion = p1 + p2

    df_fusionada = df[~df["empresa"].isin([empresa1, empresa2])].copy()

    nueva_fila = pd.DataFrame({
        "empresa": [f"{empresa1}-{empresa2}"],
        "participacion_normalizada": [nueva_participacion]
    })

    df_fusionada = pd.concat([df_fusionada, nueva_fila], ignore_index=True)

    # IHH después de la fusión
    ihh_despues = (df_fusionada["participacion_normalizada"] ** 2).sum()

    # Escalar a 10,000
    ihh_antes *= 10000
    ihh_despues *= 10000
    variacion = ihh_despues - ihh_antes

    # Mostrar resultado con estilo
    print("\n" + "-"*40)
    print("RESULTADO DE LA FUSIÓN".center(40))
    print("-"*40)
    print(f"{'IHH antes de la fusión:':<30}{round(ihh_antes, 2):>9}")
    print(f"{'IHH después de la fusión:':<30}{round(ihh_despues, 2):>9}")
    print(f"{'Variación del IHH:':<30}{round(variacion, 2):>9}")
    print("-"*40)

    return {
        "ihh_antes": float(round(ihh_antes, 2)),
        "ihh_despues": float(round(ihh_despues, 2)),
        "variacion_ihh": float(round(variacion, 2))
    }


def calcular_id_interactivo():
    import pandas as pd

    print("Cálculo del Índice de Dominancia (ID)\n")

    # Modo de entrada de datos
    modo = input("¿Quieres usar un DataFrame (d) o ingresar manualmente (m)? [d/m]: ").strip().lower()
    if modo not in ["d", "m"]:
        raise ValueError("Opción inválida. Escribe 'd' para DataFrame o 'm' para manual.")

    # Tipo de dato
    tipo_dato = input("¿Qué tipo de dato vas a ingresar? Escribe 'porcentaje' o 'valores': ").strip().lower()
    if tipo_dato not in ["porcentaje", "valores"]:
        raise ValueError("tipo_dato debe ser 'porcentaje' o 'valores'.")

    # Obtener DataFrame
    if modo == "d":
        ruta = input("Ruta del archivo CSV con columnas 'empresa' y 'participacion': ").strip()
        df = pd.read_csv(ruta)

        if not {'empresa', 'participacion'}.issubset(df.columns):
            raise ValueError("El archivo debe contener las columnas 'empresa' y 'participacion'.")

    else:
        n = int(input("¿Cuántas empresas quieres ingresar? "))
        empresas = []
        participaciones = []

        for i in range(n):
            nombre = input(f"Nombre de la empresa {i+1}: ").strip()
            etiqueta = "Participación (%)" if tipo_dato == "porcentaje" else "Valor absoluto"
            valor = float(input(f"{etiqueta} de '{nombre}': "))
            empresas.append(nombre)
            participaciones.append(valor)

        df = pd.DataFrame({
            "empresa": empresas,
            "participacion": participaciones
        })

    participaciones = df["participacion"].copy()

    if tipo_dato == "porcentaje":
        if participaciones.sum() > 100:
            raise ValueError("La suma de las participaciones supera el 100%. Verifica tus datos.")
        participaciones = participaciones / 100

    elif tipo_dato == "valores":
        total = participaciones.sum()
        if total == 0:
            raise ValueError("La suma de los valores es cero. No se puede calcular el índice.")
        participaciones = participaciones / total

    # Ordenar de mayor a menor para obtener s1 y el resto
    participaciones_ordenadas = participaciones.sort_values(ascending=False).reset_index(drop=True)
    s1 = participaciones_ordenadas.iloc[0]
    suma_restantes = participaciones_ordenadas.iloc[1:].sum()

    if suma_restantes == 0:
        raise ValueError("No hay empresas además de la dominante. No se puede calcular el índice de dominancia.")

    id_dominancia = (s1 / suma_restantes)*10000

    print("\n--- RESULTADO ---")
    print("Índice de Dominancia (ID):", round(id_dominancia, 2))


def calcular_ihh_interactivo():
    import pandas as pd

    print("Cálculo del Índice Herfindahl-Hirschman (IHH)\n")

    # Modo de entrada de datos
    modo = input("¿Quieres usar un DataFrame (d) o ingresar manualmente (m)? [d/m]: ").strip().lower()
    if modo not in ["d", "m"]:
        raise ValueError("Opción inválida. Escribe 'd' para DataFrame o 'm' para manual.")

    # Tipo de dato
    tipo_dato = input("¿Qué tipo de dato vas a ingresar? Escribe 'porcentaje' o 'valores': ").strip().lower()
    if tipo_dato not in ["porcentaje", "valores"]:
        raise ValueError("tipo_dato debe ser 'porcentaje' o 'valores'.")


    # Obtener DataFrame
    if modo == "d":
        ruta = input("Ruta del archivo CSV con columnas 'empresa' y 'participacion': ").strip()
        df = pd.read_csv(ruta)

        if not {'empresa', 'participacion'}.issubset(df.columns):
            raise ValueError("El archivo debe contener las columnas 'empresa' y 'participacion'.")

    else:
        # Ingreso manual
        n = int(input("¿Cuántas empresas quieres ingresar? "))
        empresas = []
        participaciones = []

        for i in range(n):
            nombre = input(f"Nombre de la empresa {i+1}: ").strip()
            etiqueta = "Participación (%)" if tipo_dato == "porcentaje" else "Valor absoluto"
            valor = float(input(f"{etiqueta} de '{nombre}': "))
            empresas.append(nombre)
            participaciones.append(valor)

        df = pd.DataFrame({
            "empresa": empresas,
            "participacion": participaciones
        })

    # Validaciones y cálculo
    participaciones = df["participacion"].copy()

    if tipo_dato == "porcentaje":
        if participaciones.sum() > 100:
            raise ValueError("La suma de las participaciones supera el 100%. Verifica tus datos.")
        participaciones = participaciones / 100

    elif tipo_dato == "valores":
        total = participaciones.sum()
        if total == 0:
            raise ValueError("La suma de los valores es cero. No se puede calcular el IHH.")
        participaciones = participaciones / total

    # Cálculo del IHH
    ihh = (participaciones ** 2).sum()
    resultado = ihh * 10000

    print("\n--- RESULTADO ---")
    print("Índice Herfindahl-Hirschman (IHH):", round(resultado, 2))