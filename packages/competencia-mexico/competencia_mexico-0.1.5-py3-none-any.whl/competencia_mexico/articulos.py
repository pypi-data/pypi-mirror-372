# utils.py (o el módulo que prefieras)
def buscar_articulos_csv(palabra_clave):
    """
    Busca artículos que contengan la palabra clave en el CSV empaquetado
    'articulos_final.csv' (incluido dentro de competencia_mexico/data).

    Retorna:
        pd.DataFrame con columnas ['articulo_titulo', 'texto'] filtradas.
    """
    import pandas as pd
    import re

    try:
        # Python 3.9+: acceso a recursos empacados
        from importlib.resources import files
        data_path = files('competencia_mexico.data').joinpath('articulos_final.csv')
        df = pd.read_csv(data_path)
    except Exception as e:
        # Fallback para entornos viejos o si falla importlib.resources
        try:
            import pkgutil, io
            raw = pkgutil.get_data('competencia_mexico.data', 'articulos_final.csv')
            if raw is None:
                raise FileNotFoundError("No se encontró 'articulos_final.csv' en los recursos del paquete.")
            df = pd.read_csv(io.BytesIO(raw))
        except Exception as e2:
            print(f"❌ No pude cargar el CSV empaquetado: {e2}")
            import pandas as pd
            return pd.DataFrame(columns=["articulo_titulo", "texto"])

    # Validación de columnas
    if not {"articulo_titulo", "texto"}.issubset(df.columns):
        raise ValueError("El CSV debe contener las columnas 'articulo_titulo' y 'texto'.")

    # Filtrar por palabra clave (búsqueda insensible a mayúsculas)
    coincidencias = df[df['texto'].str.contains(palabra_clave, case=False, na=False)].copy()

    if coincidencias.empty:
        print(f"\n🔍 No se encontraron artículos que contengan: '{palabra_clave}'")
        return pd.DataFrame(columns=["articulo_titulo", "texto"])

    # Mostrar títulos
    print(f"\n📄 Los artículos donde aparece lo que buscas ('{palabra_clave}') son:\n")
    for titulo in coincidencias["articulo_titulo"]:
        print(f"• {titulo}")

    # Interactivo: mostrar texto completo con resaltado
    ver_textos = input("\n¿Deseas ver el texto completo con las coincidencias resaltadas? (s/n): ").strip().lower()
    if ver_textos == "s":
        patron = re.compile(re.escape(palabra_clave), re.IGNORECASE)
        def resaltar(txt):
            return patron.sub(lambda m: f"\033[1m{m.group(0)}\033[0m", txt)

        for _, fila in coincidencias.iterrows():
            print(f"\n\033[94m{fila['articulo_titulo']}\033[0m")
            print(resaltar(str(fila['texto'])))
            print("-" * 60)

    return coincidencias[["articulo_titulo", "texto"]]

