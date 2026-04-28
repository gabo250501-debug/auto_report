# Generador Automático de Reportes (Auto Report)

Este proyecto es un sistema de automatización en Python diseñado para convertir datos crudos industriales (archivos CSV o Excel) en **reportes ejecutivos en formato PDF**. Permite analizar métricas clave como el consumo eléctrico, horas operativas y fallas detectadas en diversos equipos, presentando la información en tablas estructuradas y visualizaciones gráficas de alta calidad.

## 🚀 Funciones y Características

- **Interfaz Gráfica Amigable:** Incluye una interfaz de usuario (GUI) desarrollada con `tkinter` que permite a cualquier usuario, incluso sin conocimientos de programación, seleccionar archivos y generar reportes con un par de clics.
- **Procesamiento de Datos:** Utiliza `pandas` para leer archivos (`.csv`, `.xlsx`, `.xls`), limpiar los datos y realizar agregaciones (totales y promedios por equipo).
- **Visualización Estadística:** Genera automáticamente gráficos de barras con `matplotlib` para visualizar el consumo de energía por equipo, utilizando un diseño limpio y moderno que evita el solapamiento de datos.
- **Reportes Ejecutivos en PDF:** Compila la información procesada y los gráficos en un documento PDF profesional utilizando `fpdf2`, con encabezados, tablas con diseño "cebra" y paginación.
- **Generador de Datos de Prueba:** Incluye un script secundario para simular datos industriales y facilitar las pruebas del sistema sin necesidad de contar con datos reales.

## 📂 Estructura del Proyecto

- `app.py`: Archivo principal que ejecuta la interfaz gráfica (GUI) de la aplicación.
- `generar_reporte.py`: Módulo principal que contiene la lógica de procesamiento de datos, creación del gráfico y compilación del archivo PDF.
- `generador_datos.py`: Script para generar el archivo `datos_proyecto.csv` con datos aleatorios simulados de equipos industriales.
- `requirements.txt`: Lista de dependencias y librerías de Python necesarias para ejecutar el proyecto.
- `datos_proyecto.csv`: (Generado) Archivo de prueba con el registro diario de equipos, consumo, horas y fallas.
- `grafico_consumo.png`: (Generado) Imagen temporal del gráfico utilizado para incrustar en el PDF.

## 🛠️ Requisitos e Instalación

1. Asegúrate de tener Python instalado (versión 3.8 o superior recomendada).
2. Clona o descarga este repositorio.
3. (Opcional) Crea y activa un entorno virtual.
4. Instala las dependencias necesarias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Cómo Usar el Sistema

1. **(Opcional) Generar datos de prueba:**
   Si no tienes un archivo CSV/Excel propio, puedes generar uno ejecutando:
   ```bash
   python generador_datos.py
   ```
   Esto creará un archivo llamado `datos_proyecto.csv` con simulaciones de casi dos años de operación.

2. **Iniciar la Aplicación:**
   Ejecuta el archivo de la interfaz gráfica:
   ```bash
   python app.py
   ```

3. **Generar el Reporte:**
   - En la ventana que se abre, haz clic en **"Cargar Archivo"** y selecciona tu archivo de datos (por ejemplo, el `datos_proyecto.csv` generado anteriormente).
   - Haz clic en **"Generar Reporte PDF"**.
   - Elige la ubicación y el nombre con el que deseas guardar tu reporte.
   - ¡Listo! La aplicación te notificará cuando el reporte ejecutivo haya sido creado exitosamente.

## 📝 Notas Extra

- **Personalización Visual:** Si deseas cambiar los colores corporativos del reporte PDF o de los gráficos, puedes editar las variables constantes al inicio del archivo `generar_reporte.py` (ej. `COLOR_PRIMARIO`).
- **Escalabilidad:** El script de `pandas` está preparado para manejar eficientemente grandes volúmenes de datos. Puedes agregar más columnas a tu archivo de origen, pero requerirás ajustar la función `procesar_datos()` en `generar_reporte.py` para mapearlas correctamente en el PDF final.
