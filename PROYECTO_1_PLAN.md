# Proyecto 1: Generador Automático de Reportes (Auto Report) - Plan de Desarrollo

## 1. Interpretación del Problema
En las plantas industriales, los supervisores pierden horas semanales consolidando datos de consumo y fallas en reportes manuales. Este proceso es lento y el formato suele ser inconsistente. La automatización de reportes ejecutivos en PDF garantiza que la gerencia reciba información precisa, visual y estructurada en segundos, facilitando la rendición de cuentas y la detección de desviaciones.

## 2. Lógica de Negocio
*   **Agregación por Equipo:** El sistema agrupa los registros diarios por equipo para calcular totales y promedios de consumo energético, horas operativas y fallas detectadas.
*   **KPIs Visuales:** Gráfico de barras del consumo total por equipo con etiquetas de valor, colores diferenciados y diseño minimalista (sin bordes superiores/derechos).
*   **Formato Ejecutivo:** Tablas con efecto "cebra" (filas alternadas), encabezados con color primario, línea separadora y paginación automática.

## 3. Arquitectura del Sistema
*   **Frontend (`app.py` — Tkinter):** Interfaz gráfica de 2 pasos:
    *   Paso 1: Selección de archivo CSV/XLS/XLSX mediante `filedialog`.
    *   Paso 2: Generación y guardado del PDF con `filedialog.asksaveasfilename`.
    *   Manejo de estados: botón "Generar" deshabilitado hasta que haya archivo cargado, cursor de espera durante procesamiento.
*   **Backend (`generar_reporte.py` — Pandas + Matplotlib + fpdf2):**
    *   `procesar_datos()`: Carga CSV/Excel, agrupa por `Equipo` y calcula sumas/promedios de `Consumo_kWh`, `Horas_Operativas`, `Fallas_Detectadas`.
    *   `generar_grafico()`: Crea gráfico de barras con colores corporativos y lo guarda como PNG.
    *   `generar_pdf()`: Compila tabla de datos + gráfico en un PDF ejecutivo usando la clase `ReportePDF(FPDF)` con header/footer personalizados.
    *   `main()`: Orquesta el flujo completo (datos → gráfico → PDF).

## 4. Columnas del Dataset Esperado

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Fecha` | `date` | Fecha del registro diario |
| `Equipo` | `str` | Nombre del equipo (Motor_Principal, Compresor_A, etc.) |
| `Consumo_kWh` | `float` | Consumo energético en kWh |
| `Horas_Operativas` | `int` | Horas de operación del día |
| `Fallas_Detectadas` | `int` | Número de fallas registradas |

---

## 🌟 FASE DE MEJORA: RUMBO A LAS 5 ESTRELLAS

### 🛠️ Mejoras Técnicas Identificadas
1.  ✅ **Gestión de Archivos Temporales:** Gráfico ahora se genera con `tempfile.NamedTemporaryFile` y se elimina tras insertar en el PDF. Ya no contamina el CWD.
2.  ✅ **Soporte Multi-Página:** Método `tabla_con_paginacion()` en `ReportePDF` — detecta el final de página y repite encabezados automáticamente.
3.  ✅ **Robustez de Ingesta:** Detección de encoding con `chardet` + fallback a `latin-1`. Validación de columnas requeridas con error descriptivo.
4.  ✅ **Logging Profesional:** Todos los `print()` reemplazados por `logging` con niveles INFO/WARNING/ERROR y timestamps.
5.  ✅ **Validación de Columnas:** `procesar_datos()` ahora valida que existan `Equipo`, `Consumo_kWh`, `Horas_Operativas`, `Fallas_Detectadas` antes de procesar.
6.  ✅ **Type Hints:** Anotaciones de tipo en todas las funciones de `generar_reporte.py` y `app.py`.
7.  ✅ **Tests Unitarios:** 17 tests en `tests/test_generar_reporte.py` (pytest) — 100% passing. Cubre: ingesta, cálculos, gráficos, PDF, flujo completo y limpieza de temporales.

### 💡 Mejoras Adicionales Implementadas
*   **Sección de KPIs** en el PDF (consumo total, horas, fallas, equipo crítico).
*   **Conteo total de páginas** con `alias_nb_pages()` → "Página 1/3".
*   **Formato de miles** en números del PDF (ej. `1,234.56`).
*   **GUI mejorada:** barra de estado, emojis informativos, tamaño de archivo, versión en footer.
*   **Manejo de errores granular** en la GUI (FileNotFoundError, ValueError, genérico).

### 💼 Enfoque de Servicio (Futuro)
*   **Personalización de Marca:** Permitir al cliente subir su propio logo y elegir colores corporativos.
*   **Envío Automático:** Enviar el reporte por correo electrónico al finalizar.

**Estado:** ⭐⭐⭐⭐⭐ Mejoras completadas — 17/17 tests passing.
