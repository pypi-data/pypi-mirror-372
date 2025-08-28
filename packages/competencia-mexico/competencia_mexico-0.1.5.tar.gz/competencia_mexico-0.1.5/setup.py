# setup.py
from setuptools import setup, find_packages
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="competencia_mexico",
    version="0.1.5",
    author="Iván Paredes Reséndiz",
    author_email="",
    description="Herramientas para análisis de competencia, precios, visualización y RAG (FAISS + DeepSeek).",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/IvanParedesR/competencia_mexico",
    project_urls={
        "Bug Tracker": "https://github.com/IvanParedesR/competencia_mexico/issues",
        "Documentation": "https://github.com/IvanParedesR/competencia_mexico",
    },
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,  # <-- importante para empaquetar data
    package_data={
        "competencia_mexico": [
            "data/*.csv",              # p.ej. articulos_final.csv, estadisticas_final.csv
            "faiss_index/*",         # si algún día incluyes un índice FAISS dentro del paquete (no es lo ideal)
        ]
    },
    install_requires=[
        "pandas>=1.3",
        "matplotlib>=3.5",
        "numpy>=1.21",
        "requests>=2.28",
        "langchain-community>=0.2.0",
        "sentence-transformers>=2.5.0",
        "faiss-cpu>=1.7.4",        # si vas a construir/cargar índices FAISS en el runtime
    ],
    extras_require={
        "dev": ["pytest", "ruff", "black", "twine", "build"],
        "rag": ["faiss-cpu>=1.7.4"],  # instala con: pip install competencia_tools[rag]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    entry_points={
        # Opcional: atajos en terminal para lanzar funciones interactivas
        "console_scripts": [
            # "competencia-ihh=competencia_tools.indices:calcular_ihh_interactivo",
            # "competencia-asuntos=competencia_tools.graficos:graficar_y_resumir_asuntos_interactiva",
            # "competencia-rag=competencia_tools.rag:consultar_con_rag_deepseek",
        ]
    },
    zip_safe=False,  # más seguro si lees data con métodos tradicionales; con importlib.resources no es obligatorio
)








