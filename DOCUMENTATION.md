# Casalia - Documentación del Proyecto

## Descripción General
**Casalia** es una plataforma web inteligente diseñada para la predicción de precios inmobiliarios a 12 meses vista en España. Se basa en el uso de Inteligencia Artificial para ofrecer estimaciones transparentes a partir de datos del Instituto Nacional de Estadística (INE), como tasas demográficas e indicadores macroeconómicos.

## Estructura del Proyecto

El proyecto está dividido en dos grandes bloques tecnológicos: el motor de Machine Learning (backend) y la interfaz de usuario (frontend).

### 1. Backend & Machine Learning (`/ml`)
Desarrollado en **Python**, el motor predictivo se encarga de todo el procesamiento de datos, entrenamiento del modelo y exposición del servicio.

*   **Stack:** PyTorch, FastAPI, Pandas, Scikit-learn, Uvicorn.
*   **Pipeline de Datos (`prepare_data.py`, `train.py`):** Ingesta de datos crudos, creación de características (incluyendo rezagos temporales e histórico de variaciones macroeconómicas) y generación de modelos normalizados.
*   **El Modelo (`model.py`):** Un Perceptrón Multicapa (MLP) en PyTorch entrenado para inferir dinámicas de precios a un año vista con alta fiabilidad, huyendo de las "cajas negras" tradicionales y aportando transparencia (explainable AI).
*   **La API (`app/main.py`):** Expone un servidor web ligero con FastAPI que responde al endpoint `/predict`. Recibe datos como *comunidad autónoma*, *precio total* y *metros cuadrados*, y devuelve la estimación futura.

### 2. Frontend (`/web`)
Una Single Page Application (SPA) desarrollada para ofrecer una experiencia interactiva, responsiva y multilingüe.

*   **Stack:** React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, i18next.
*   **Arquitectura Visual:** Estética "Neo-Brutalista" que transmite solidez y claridad. Utiliza animaciones fluidas (Framer Motion) para hacer la inferencia visualmente atractiva.
*   **Componentes Clave:**
    *   `Estimator.tsx`: Formulario interactivo que conecta directamente con la API en FastAPI para mostrar resultados de inferencia en tiempo real.
    *   `Methodology.tsx` / `SegmentsFAQ.tsx`: Secciones que explican al usuario cómo funciona la red neuronal por debajo, aportando valor añadido y confianza al producto.

## Despliegue y Ejecución Local

### Requisitos Previos
*   Python 3.10+
*   Node.js 20+

### Levantar el Backend (API)
```bash
cd ml
python -m venv .venv
# Activar entorno (Windows): .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Levantar el Frontend (Web)
```bash
cd web
npm install
npm run dev
```
La aplicación web estará disponible en github.
