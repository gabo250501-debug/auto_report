import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# Configuraciones de diseño del reporte
COLOR_PRIMARIO = (41, 128, 185)  # Azul ejecutivo
COLOR_FONDO_TABLA = (236, 240, 241) # Gris claro
COLOR_TEXTO = (44, 62, 80) # Gris oscuro

class ReportePDF(FPDF):
    def header(self):
        # Título del documento
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(*COLOR_PRIMARIO)
        self.cell(0, 15, 'Reporte Ejecutivo de Rendimiento de Equipos', align='C', new_x='LMARGIN', new_y='NEXT')
        
        # Fecha de generación
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(*COLOR_TEXTO)
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        self.cell(0, 10, f'Fecha de generación: {fecha_actual}', align='C', new_x='LMARGIN', new_y='NEXT')
        
        # Línea separadora
        self.set_draw_color(*COLOR_PRIMARIO)
        self.set_line_width(0.5)
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        # Número de página
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def procesar_datos(ruta_archivo):
    """
    Carga y procesa el archivo CSV, calculando métricas clave como totales y promedios.
    """
    try:
        # Cargar datos con pandas dependiendo de la extensión
        if ruta_archivo.lower().endswith('.csv'):
            df = pd.read_csv(ruta_archivo)
        elif ruta_archivo.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(ruta_archivo)
        else:
            raise ValueError("Formato de archivo no soportado. Por favor, cargue un archivo .csv o .xlsx")
        
        print("Datos cargados exitosamente.")
        
        # Calcular totales y promedios por equipo
        resumen = df.groupby('Equipo').agg({
            'Consumo_kWh': ['sum', 'mean'],
            'Horas_Operativas': ['sum', 'mean'],
            'Fallas_Detectadas': 'sum'
        }).reset_index()
        
        # Aplanar los nombres de las columnas multinivel
        resumen.columns = ['Equipo', 'Consumo Total (kWh)', 'Consumo Promedio (kWh)', 
                           'Horas Totales', 'Horas Promedio', 'Fallas Totales']
        
        # Redondear valores numéricos a 2 decimales para una mejor presentación
        resumen = resumen.round(2)
        return resumen
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo '{ruta_archivo}' no fue encontrado. Verifique la ruta.")
    except Exception as e:
        raise Exception(f"Error inesperado al procesar los datos: {e}")

def generar_grafico(df, ruta_salida):
    """
    Genera un gráfico de barras del consumo total por equipo y lo guarda como imagen.
    """
    # Aumentamos el tamaño de la figura para dar más espacio
    plt.figure(figsize=(12, 6))
    
    # Colores elegantes para el gráfico
    colores = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    
    # Asegurar que no faltan colores si hay más equipos
    if len(df) > len(colores):
        colores = colores * (len(df) // len(colores) + 1)
        
    barras = plt.bar(df['Equipo'], df['Consumo Total (kWh)'], color=colores[:len(df)])
    
    # Personalización del gráfico
    plt.title('Consumo Total de Energía (kWh) por Equipo', fontsize=16, pad=15)
    plt.xlabel('Equipos', fontsize=12)
    plt.ylabel('Consumo (kWh)', fontsize=12)
    
    # Rotar las etiquetas 45 grados y alinearlas a la derecha para que no se encimen
    plt.xticks(rotation=45, ha='right', fontsize=11) 
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Añadir etiquetas de valor sobre las barras
    for barra in barras:
        alto = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2., alto + (alto * 0.01),
                 f'{alto:,.0f}',
                 ha='center', va='bottom', fontsize=11)
    
    # Eliminar bordes superior y derecho para un diseño más limpio (estilo minimalista)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=300)
    plt.close()
    print(f"Gráfico generado exitosamente en '{ruta_salida}'.")

def generar_pdf(df_resumen, ruta_grafico, ruta_salida):
    """
    Genera un reporte PDF con diseño ejecutivo, integrando la tabla de datos y el gráfico.
    """
    pdf = ReportePDF()
    pdf.add_page()
    
    # Sección 1: Resumen de Datos (Tabla)
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(*COLOR_TEXTO)
    pdf.cell(0, 10, '1. Resumen de Rendimiento por Equipo', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)
    
    # Configuración de la tabla
    columnas = list(df_resumen.columns)
    # Definir anchos adaptados a los nombres de las columnas (total: 190 mm)
    anchos = [35, 35, 40, 25, 30, 25]  
    
    # Encabezado de la tabla
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_fill_color(*COLOR_PRIMARIO)
    pdf.set_text_color(255, 255, 255)
    
    for col, ancho in zip(columnas, anchos):
        # MultiCell sería mejor si hay saltos de línea, pero simplificaremos con Cell
        pdf.cell(ancho, 8, col, border=1, align='C', fill=True)
    pdf.ln()
    
    # Filas de la tabla con efecto cebra
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(*COLOR_TEXTO)
    
    fill = False
    for _, fila in df_resumen.iterrows():
        if fill:
            pdf.set_fill_color(*COLOR_FONDO_TABLA)
        else:
            pdf.set_fill_color(255, 255, 255)
            
        for valor, ancho in zip(fila, anchos):
            # Formatear números para mejor presentación
            if isinstance(valor, float):
                str_valor = f"{valor:.2f}"
            else:
                str_valor = str(valor)
            pdf.cell(ancho, 8, str_valor, border=1, align='C', fill=fill)
        pdf.ln()
        fill = not fill
        
    pdf.ln(10)
    
    # Sección 2: Visualización de Datos (Gráfico)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Visualización Estadística', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    
    # Calcular posición centrada para la imagen
    ancho_pagina = pdf.w - 2 * pdf.l_margin
    ancho_imagen = 140
    x_imagen = (ancho_pagina - ancho_imagen) / 2 + pdf.l_margin
    
    try:
        # Insertar gráfico guardado previamente
        pdf.image(ruta_grafico, x=x_imagen, w=ancho_imagen)
    except Exception as e:
        print(f"Advertencia: No se pudo insertar la imagen en el PDF. {e}")
        pdf.set_font('helvetica', 'I', 10)
        pdf.cell(0, 10, '(Error al cargar el gráfico)', align='C', new_x='LMARGIN', new_y='NEXT')
        
    # Guardar documento final
    try:
        pdf.output(ruta_salida)
        print(f"Reporte PDF ejecutivo generado exitosamente: '{ruta_salida}'.")
    except Exception as e:
        print(f"Error al guardar el reporte PDF: {e}")

def main(archivo_entrada='datos_proyecto.csv', archivo_pdf='Reporte_Ejecutivo.pdf'):
    """
    Función principal que orquesta el flujo de ejecución.
    """
    archivo_grafico = 'grafico_consumo.png'
    
    print("Iniciando automatización de reportes...")
    
    # 1. Cargar y transformar datos
    df_resumen = procesar_datos(archivo_entrada)
    
    # 2. Generar representación visual (Gráfico)
    generar_grafico(df_resumen, archivo_grafico)
    
    # 3. Compilar en documento final (PDF)
    generar_pdf(df_resumen, archivo_grafico, archivo_pdf)
    
    print("¡Automatización completada con éxito!")

if __name__ == '__main__':
    main()
