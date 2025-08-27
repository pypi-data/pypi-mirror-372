def consultar_con_rag_deepseek():
    """
    Consulta un sistema RAG local usando DeepSeek.
    El índice FAISS está incluido en la carpeta 'data/faiss_index' del paquete.
    """

    # === Imports locales para evitar carga innecesaria si no se usa ===
    import requests
    import pickle
    from pathlib import Path
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings

    # Paso 1: Solicitar API Key y pregunta
    print("🔐 Bienvenido al sistema RAG con DeepSeek")
    api_key = input("➡️ Ingresa tu API Key de DeepSeek: ").strip()
    pregunta = input("❓ Escribe tu pregunta: ").strip()

    # Paso 2: Definir ruta interna del índice FAISS
    index_dir = Path(__file__).parent / "data" / "faiss_index"
    index_name = "faiss_index"
    index_path = index_dir / f"{index_name}.pkl"

    if not index_path.exists():
        print(f"❌ No se encontró el índice FAISS en {index_path}")
        return

    # Paso 3: Cargar índice FAISS
    print("📂 Cargando índice FAISS incluido en el paquete...")
    with open(index_path, "rb") as f:
        _ = pickle.load(f)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(
        folder_path=index_dir,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

    # Paso 4: Buscar documentos relevantes
    print("🔍 Buscando fragmentos relevantes...")
    documentos = db.similarity_search(pregunta, k=3)
    contexto = "\n\n".join([doc.page_content for doc in documentos])
    fuentes = [(doc.metadata.get("source", "desconocido"), doc.metadata.get("paragraph", "?"))
               for doc in documentos]

    # Paso 5: Crear prompt y consultar DeepSeek
    prompt = f"""Responde con base en el siguiente contexto. Al final, menciona el documento y párrafos usados como fuente.

Contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:"""

    print("🤖 Consultando modelo DeepSeek...")
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error consultando la API de DeepSeek: {e}")
        return

    respuesta = response.json()["choices"][0]["message"]["content"]

    # Paso 6: Mostrar respuesta y fuentes
    print("\n🧠 Respuesta:")
    print(respuesta.strip())

    print("\n📚 Fuentes:")
    for src, p in fuentes:
        print(f"- {src}, párrafo {p}")
