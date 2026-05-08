"""
Generador Automático de Reportes Ejecutivos Industriales
=========================================================
Proyecto 1 - Portafolio IIoT

Transforma datos crudos de equipos industriales (CSV/Excel) en reportes
ejecutivos PDF con tablas de resumen y visualizaciones estadísticas.

Mejoras v2.0:
- Logging profesional (reemplaza print)
- Archivos temporales para gráficos (tempfile)
- Soporte multi-página para tablas extensas
- Detección de encoding para CSVs latinoamericanos
- Type hints en todas las funciones
- Manejo de errores granular
"""

import os
import logging
import tempfile
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ============================================================================
# CONFIGURACIONES DE DISEÑO DEL REPORTE
# ============================================================================
COLOR_PRIMARIO = (41, 128, 185)       # Azul ejecutivo
COLOR_SECUNDARIO = (52, 152, 219)     # Azul claro (encabezados de sección)
COLOR_FONDO_TABLA = (236, 240, 241)   # Gris claro (filas alternas)
COLOR_TEXTO = (44, 62, 80)            # Gris oscuro
COLOR_EXITO = (39, 174, 96)           # Verde (indicadores positivos)
COLOR_ALERTA = (231, 76, 60)          # Rojo (indicadores negativos)

COLORES_GRAFICO = ['#2980b9', '#e74c3c', '#27ae60', '#f39c12', '#8e44ad',
                   '#1abc9c', '#d35400', '#2c3e50', '#16a085', '#c0392b']

ROW_HEIGHT = 8          # Altura de fila en la tabla (mm)
PAGE_BOTTOM_MARGIN = 25  # Margen inferior antes de saltar de página (mm)


# ============================================================================
# CLASE DE REPORTE PDF CON SOPORTE MULTI-PÁGINA
# ============================================================================
class ReportePDF(FPDF):
    """Clase PDF ejecutiva con header/footer corporativos y soporte multi-página."""

    def header(self) -> None:
        """Encabezado corporativo en cada página."""
        # Título del documento
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(*COLOR_PRIMARIO)
        self.cell(0, 15, 'Reporte Ejecutivo de Rendimiento de Equipos',
                  align='C', new_x='LMARGIN', new_y='NEXT')

        # Fecha de generación
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(*COLOR_TEXTO)
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.cell(0, 10, f'Fecha de generación: {fecha_actual}',
                  align='C', new_x='LMARGIN', new_y='NEXT')

        # Línea separadora
        self.set_draw_color(*COLOR_PRIMARIO)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self) -> None:
        """Pie de página con número de página y crédito."""
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    def _escribir_encabezado_tabla(self, columnas: list[str],
                                   anchos: list[int]) -> None:
        """Dibuja la fila de encabezado de la tabla con estilo corporativo."""
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(*COLOR_PRIMARIO)
        self.set_text_color(255, 255, 255)
        for col, ancho in zip(columnas, anchos):
            self.cell(ancho, ROW_HEIGHT, col, border=1, align='C', fill=True)
        self.ln()
        # Restaurar color de texto para las filas
        self.set_text_color(*COLOR_TEXTO)
        self.set_font('helvetica', '', 9)

    def tabla_con_paginacion(self, df: pd.DataFrame,
                             anchos: list[int]) -> None:
        """Renderiza una tabla con salto de página automático y encabezado
        repetido en cada nueva página.

        Args:
            df: DataFrame con los datos a renderizar.
            anchos: Lista de anchos de columna en mm.
        """
        columnas = list(df.columns)
        self._escribir_encabezado_tabla(columnas, anchos)

        fill = False
        for _, fila in df.iterrows():
            # Verificar si queda espacio en la página actual
            if self.get_y() + ROW_HEIGHT > self.h - PAGE_BOTTOM_MARGIN:
                self.add_page()
                self._escribir_encabezado_tabla(columnas, anchos)
                fill = False

            # Color alterno (efecto cebra)
            if fill:
                self.set_fill_color(*COLOR_FONDO_TABLA)
            else:
                self.set_fill_color(255, 255, 255)

            for valor, ancho in zip(fila, anchos):
                if isinstance(valor, float):
                    str_valor = f"{valor:,.2f}"
                elif isinstance(valor, int):
                    str_valor = f"{valor:,}"
                else:
                    str_valor = str(valor)
                self.cell(ancho, ROW_HEIGHT, str_valor, border=1,
                          align='C', fill=fill)
            self.ln()
            fill = not fill


# ============================================================================
# FASE 1: INGESTA Y PROCESAMIENTO DE DATOS
# ============================================================================
def _detectar_encoding(ruta_archivo: str) -> str:
    """Detecta el encoding de un archivo CSV para evitar errores con
    caracteres especiales latinoamericanos (ñ, acentos, etc.).

    Intenta chardet si está disponible, sino usa fallback seguro.
    """
    try:
        import chardet
        with open(ruta_archivo, 'rb') as f:
            resultado = chardet.detect(f.read(10000))
        encoding = resultado.get('encoding', 'utf-8')
        confianza = resultado.get('confidence', 0)
        logger.info(f"Encoding detectado: {encoding} (confianza: {confianza:.0%})")
        return encoding
    except ImportError:
        logger.warning("chardet no instalado. Usando fallback utf-8 → latin-1")
        return 'utf-8'


def procesar_datos(ruta_archivo: str) -> pd.DataFrame:
    """Carga y procesa el archivo de datos, calculando métricas por equipo.

    Args:
        ruta_archivo: Ruta al archivo CSV o Excel de entrada.

    Returns:
        DataFrame con resumen de KPIs por equipo.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el formato no es soportado o faltan columnas.
    """
    logger.info(f"Cargando datos desde: {os.path.basename(ruta_archivo)}")

    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(
            f"El archivo '{ruta_archivo}' no fue encontrado. Verifique la ruta."
        )

    ext = ruta_archivo.lower()

    # Carga con detección de encoding para CSV
    if ext.endswith('.csv'):
        encoding = _detectar_encoding(ruta_archivo)
        try:
            df = pd.read_csv(ruta_archivo, encoding=encoding)
        except UnicodeDecodeError:
            logger.warning(f"Fallo con encoding {encoding}, reintentando con latin-1")
            df = pd.read_csv(ruta_archivo, encoding='latin-1')
    elif ext.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(ruta_archivo)
    else:
        raise ValueError(
            "Formato de archivo no soportado. Use archivos .csv, .xls o .xlsx"
        )

    logger.info(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # Validar columnas requeridas
    columnas_requeridas = ['Equipo', 'Consumo_kWh', 'Horas_Operativas',
                           'Fallas_Detectadas']
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Columnas faltantes en el archivo: {faltantes}. "
            f"Columnas encontradas: {list(df.columns)}"
        )

    # Calcular totales y promedios por equipo
    resumen = df.groupby('Equipo').agg({
        'Consumo_kWh': ['sum', 'mean'],
        'Horas_Operativas': ['sum', 'mean'],
        'Fallas_Detectadas': 'sum'
    }).reset_index()

    # Aplanar los nombres de las columnas multinivel
    resumen.columns = ['Equipo', 'Consumo Total (kWh)', 'Consumo Promedio (kWh)',
                       'Horas Totales', 'Horas Promedio', 'Fallas Totales']

    resumen = resumen.round(2)
    logger.info(f"Resumen generado: {len(resumen)} equipos analizados")
    return resumen


# ============================================================================
# FASE 2: VISUALIZACIÓN
# ============================================================================
def generar_grafico(df: pd.DataFrame, ruta_salida: str) -> None:
    """Genera un gráfico de barras del consumo total por equipo.

    Args:
        df: DataFrame con la columna 'Consumo Total (kWh)' por equipo.
        ruta_salida: Ruta donde se guardará el PNG del gráfico.
    """
    logger.info("Generando gráfico de consumo energético...")

    fig, ax = plt.subplots(figsize=(12, 6))

    # Asegurar que hay suficientes colores para todos los equipos
    n_equipos = len(df)
    colores = (COLORES_GRAFICO * ((n_equipos // len(COLORES_GRAFICO)) + 1))[:n_equipos]

    barras = ax.bar(df['Equipo'], df['Consumo Total (kWh)'], color=colores,
                    edgecolor='white', linewidth=0.5)

    ax.set_title('Consumo Total de Energía (kWh) por Equipo',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Equipos', fontsize=12)
    ax.set_ylabel('Consumo (kWh)', fontsize=12)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    plt.setp(ax.get_xticklabels(), ha='right')

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Etiquetas de valor sobre las barras
    for barra in barras:
        alto = barra.get_height()
        ax.text(barra.get_x() + barra.get_width() / 2., alto + (alto * 0.01),
                f'{alto:,.0f}', ha='center', va='bottom', fontsize=10,
                fontweight='bold')

    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Gráfico guardado: {ruta_salida}")


# ============================================================================
# FASE 3: COMPILACIÓN DEL REPORTE PDF
# ============================================================================
def generar_pdf(df_resumen: pd.DataFrame, ruta_grafico: str,
                ruta_salida: str) -> None:
    """Genera un reporte PDF ejecutivo con tabla multi-página y gráfico.

    Args:
        df_resumen: DataFrame con los KPIs por equipo.
        ruta_grafico: Ruta al PNG del gráfico de consumo.
        ruta_salida: Ruta de destino para el PDF final.
    """
    logger.info("Compilando reporte PDF...")

    pdf = ReportePDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- Sección 1: Tabla de Resumen ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(*COLOR_TEXTO)
    pdf.cell(0, 10, '1. Resumen de Rendimiento por Equipo',
             new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    # Anchos de columna optimizados (total: 190 mm)
    anchos = [35, 35, 40, 25, 30, 25]

    # Renderizar tabla con paginación automática
    pdf.tabla_con_paginacion(df_resumen, anchos)
    pdf.ln(10)

    # --- Sección 2: KPIs Destacados ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(*COLOR_TEXTO)
    pdf.cell(0, 10, '2. Indicadores Clave',
             new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.set_font('helvetica', '', 11)
    total_consumo = df_resumen['Consumo Total (kWh)'].sum()
    total_horas = df_resumen['Horas Totales'].sum()
    total_fallas = df_resumen['Fallas Totales'].sum()
    equipo_critico = df_resumen.loc[
        df_resumen['Fallas Totales'].idxmax(), 'Equipo'
    ]

    indicadores = [
        f"- Consumo energetico total: {total_consumo:,.2f} kWh",
        f"- Horas operativas acumuladas: {total_horas:,.2f} h",
        f"- Fallas totales registradas: {int(total_fallas)}",
        f"- Equipo con mas fallas: {equipo_critico}",
    ]
    for indicador in indicadores:
        pdf.cell(0, 7, indicador, new_x='LMARGIN', new_y='NEXT')

    pdf.ln(5)

    # --- Sección 3: Visualización ---
    # Verificar espacio o saltar página para el gráfico
    if pdf.get_y() + 90 > pdf.h - PAGE_BOTTOM_MARGIN:
        pdf.add_page()

    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '3. Visualización Estadística',
             new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    ancho_pagina = pdf.w - 2 * pdf.l_margin
    ancho_imagen = min(160, ancho_pagina)
    x_imagen = (ancho_pagina - ancho_imagen) / 2 + pdf.l_margin

    try:
        pdf.image(ruta_grafico, x=x_imagen, w=ancho_imagen)
    except Exception as e:
        logger.error(f"No se pudo insertar el gráfico en el PDF: {e}")
        pdf.set_font('helvetica', 'I', 10)
        pdf.cell(0, 10, '(Error al cargar el gráfico)',
                 align='C', new_x='LMARGIN', new_y='NEXT')

    # Guardar documento
    pdf.output(ruta_salida)
    logger.info(f"Reporte PDF generado: {ruta_salida}")


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================
def main(archivo_entrada: str = 'datos_proyecto.csv',
         archivo_pdf: str = 'Reporte_Ejecutivo.pdf') -> None:
    """Orquesta el flujo completo: datos → gráfico → PDF.

    Usa archivos temporales para el gráfico intermedio, eliminando
    artefactos del directorio de trabajo.

    Args:
        archivo_entrada: Ruta al CSV/Excel de origen.
        archivo_pdf: Ruta de destino del PDF generado.
    """
    logger.info("=" * 50)
    logger.info("  GENERADOR AUTOMÁTICO DE REPORTES v2.0")
    logger.info("=" * 50)

    # 1. Cargar y transformar datos
    df_resumen = procesar_datos(archivo_entrada)

    # 2. Generar gráfico en archivo temporal (no contamina el CWD)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        ruta_grafico_tmp = tmp.name

    try:
        generar_grafico(df_resumen, ruta_grafico_tmp)

        # 3. Compilar en documento final (PDF)
        generar_pdf(df_resumen, ruta_grafico_tmp, archivo_pdf)
    finally:
        # Limpiar archivo temporal
        if os.path.exists(ruta_grafico_tmp):
            os.remove(ruta_grafico_tmp)
            logger.info("Archivo temporal de gráfico eliminado")

    logger.info("¡Automatización completada con éxito!")


if __name__ == '__main__':
    main()
