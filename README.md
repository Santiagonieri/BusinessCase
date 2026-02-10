# Business Case 

Este proyecto procesa información de sesiones de Google Analytics y datos del sistema transaccional con el objetivo de construir datasets finales para el análisis de KPIs en Power BI.

El flujo está diseñado para ser modular, escalable y fácilmente adaptable a cambios en las reglas de negocio.

---

## 📌 Objetivo del ejercicio

1. **Clasificar las sesiones de Google por canal y canal_detail** a partir de reglas de negocio configurables.
2. **Repartir las transacciones y el revenue del sistema transaccional** en función del peso de las sesiones por canal, fecha, mercado y dispositivo.

---

## 📂 Estructura del proyecto

├── src/
│   ├── extract/              # Lectura de datos de entrada
│   │   └── load_data.py
│   ├── save/                 # Escritura y guardado de outputs
│   │   └── save_data.py
│   ├── transform/            # Transformaciones y lógica de negocio
│   │   └── transform_data.py
│   └── __pycache__/           # Archivos compilados de Python (auto-generados)
├── reglas/
│   └── Reglas_De_Negocio.json # Reglas de clasificación de canal
├── data/
│   ├── raw/                  # Archivos de entrada (Excel original)
│   └── procesados/           # Datasets finales por etapa
├── notebooks/                # Análisis exploratorio (opcional)
├── main.py                   # Orquestador del proceso
├── variables.py              # Configuración de rutas y parámetros
├── PBI.Report/               # Metadatos del reporte (visuales, páginas, etc.)
├── PBI.SemanticModel/        # Modelo semántico (tablas, relaciones, medidas DAX)
├── PBI.pbip                  # Proyecto Power BI Desktop (formato PBIP)
├── requirements.txt
└── README.md



## Decisiones de negocio

1.Reglas de negocio configurables:
Las reglas se definen en un archivo JSON, permitiendo su modificación sin cambios en el código y facilitando el mantenimiento.

2.Reglas no definidas:
Cuando una regla no está definida, los campos Canal y Canal_Detail se asignan como "no identificado".

3.Referencia a otras columnas:
Si Canal_Detail debe tomar el valor de otra columna, se utiliza el formato
"columna:nombre_columna" (ej. "columna:campaign").

4.Peso por canal:
El peso de cada canal se calcula en base a las transacciones del frontal; si no existen, se utilizan las sesiones del frontal.

5.Distribución de métricas reales:
El peso del canal se utiliza para distribuir tanto el revenue real como las transacciones reales.

6.Tratamiento de nulos:
Se trabaja únicamente con registros que no contengan valores nulos.

7.Ratios de conversión:
Los ratios se calculan usando el REAL como referencia y se comparan contra el frontal para medir variaciones porcentuales.



## ⚙️ Requisitos

- Python 3.10 o superior

Librerías principales:
- pandas
- numpy
- openpyxl

---

## 🛠️ Instalación

```bash
git clone https://github.com/Santiagonieri/BusinessCase.git
cd BusinessCase



Desde la raíz del proyecto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt


## ▶️ Ejecución

python main.py


