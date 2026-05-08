# Generador Automático de Reportes (Auto Report) - v2.0

Este proyecto es un sistema de automatización en Python diseñado para convertir datos crudos industriales (archivos CSV o Excel) en **reportes ejecutivos en formato PDF**. Permite analizar métricas clave como el consumo eléctrico, horas operativas y fallas detectadas en diversos equipos, presentando la información en tablas estructuradas y visualizaciones gráficas de alta calidad.

## 🏭 Contexto y Problemática

En entornos industriales, el seguimiento del rendimiento de equipos se realiza frecuentemente de forma manual: técnicos exportan datos de sistemas como SAP PM, los copian en Excel y construyen tablas y gráficos a mano. Este proceso puede tomar horas, es propenso a errores humanos y dificulta la toma de decisiones oportuna.

## ✅ Solución

Este sistema automatiza completamente ese flujo. Con un par de clics, cualquier técnico o supervisor puede convertir un archivo de datos en un reporte ejecutivo profesional listo para presentar, en segundos y sin conocimientos de programación.

## 🚀 Novedades de la Versión 2.0

- **Soporte Multi-Página:** Generación inteligente de tablas que se expanden automáticamente a múltiples páginas con encabezados repetidos.
- **Robustez en Ingesta:** Detección automática de encoding (`chardet`) para evitar errores con caracteres especiales y acentos latinoamericanos.
- **Logging Profesional:** Sistema de registro con timestamps para trazabilidad total de procesos y errores.
- **Calidad de Código:** Implementación de **Type Hints** y **Manejo de Errores Granular**.
- **Suite de Pruebas:** Incluye 17 tests unitarios automatizados con `pytest` para garantizar la fiabilidad de los cálculos.

## 🛠️ Funciones y Características

- **Interfaz Gráfica Amigable:** Incluye una interfaz de usuario (GUI) desarrollada con `tkinter` que permite a cualquier usuario seleccionar archivos y generar reportes con un par de clics.
- **Procesamiento de Datos:** Utiliza `pandas` para leer archivos (`.csv`, `.xlsx`, `.xls`), limpiar los datos y realizar agregaciones (totales y promedios por equipo).
- **Visualización Estadística:** Genera automáticamente gráficos de barras con `matplotlib` para visualizar el consumo de energía por equipo, utilizando un diseño limpio y moderno.
- **Reportes Ejecutivos en PDF:** Compila la información procesada y los gráficos en un documento PDF profesional utilizando `fpdf2`, con encabezados, tablas con diseño "cebra" y paginación.
- **Generador de Datos de Prueba:** Incluye un script secundario para simular datos industriales y facilitar las pruebas del sistema.

## 🧪 Pruebas Unitarias

Para verificar la integridad del sistema y los cálculos de KPIs:
```bash
pytest tests/ -v
```

## 📂 Estructura del Proyecto

- `app.py`: Archivo principal que ejecuta la interfaz gráfica (GUI) de la aplicación.
- `generar_reporte.py`: Módulo principal que contiene la lógica de procesamiento de datos y renderizado PDF.
- `tests/`: Carpeta con la suite de pruebas unitarias automatizadas.
- `generador_datos.py`: Script para generar el archivo `datos_proyecto.csv` con datos aleatorios simulados.
- `requirements.txt`: Lista de dependencias y librerías de Python necesarias.
- `PROYECTO_1_PLAN.md`: Documento detallado del plan de desarrollo y mejoras técnicas.

## 📖 Cómo Usar el Sistema

1. **(Opcional) Generar datos de prueba:**
   ```bash
   python generador_datos.py
   ```

2. **Iniciar la Aplicación:**
   ```bash
   python app.py
   ```

3. **Generar el Reporte:**
   - Carga tu archivo de datos (`.csv` o `.xlsx`).
   - Haz clic en **"Generar Reporte PDF"**.
   - Elige la ubicación y guarda tu reporte ejecutivo.

## 📝 Notas Extra

- **Personalización Visual:** Puedes editar las constantes al inicio de `generar_reporte.py` (ej. `COLOR_PRIMARIO`) para cambiar la estética del reporte.
- **Escalabilidad:** El sistema está preparado para manejar grandes volúmenes de datos eficientemente mediante `pandas`.

---
**Desarrollado como parte del Portafolio IIoT - Soluciones de Automatización Industrial.**
