"""
Tests Unitarios - Generador Automático de Reportes
====================================================
Proyecto 1 - Portafolio IIoT

Valida las funciones de procesamiento de datos y generación de reportes
usando datasets de prueba controlados.
"""

import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para tests

import pandas as pd
import pytest

# Agregar el directorio padre al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generar_reporte


# ============================================================================
# FIXTURES: DATOS DE PRUEBA
# ============================================================================
@pytest.fixture
def datos_basicos() -> pd.DataFrame:
    """Dataset mínimo con 3 equipos y 2 registros por equipo."""
    return pd.DataFrame({
        'Fecha': ['2024-01-01'] * 6,
        'Equipo': ['Motor_A', 'Motor_A', 'Bomba_B', 'Bomba_B',
                   'Compresor_C', 'Compresor_C'],
        'Consumo_kWh': [100.0, 150.0, 200.0, 250.0, 300.0, 350.0],
        'Horas_Operativas': [20, 22, 24, 20, 18, 16],
        'Fallas_Detectadas': [0, 1, 2, 0, 3, 1]
    })


@pytest.fixture
def csv_basico(datos_basicos: pd.DataFrame, tmp_path) -> str:
    """Guarda el dataset básico como CSV temporal y retorna la ruta."""
    ruta = tmp_path / "datos_test.csv"
    datos_basicos.to_csv(ruta, index=False)
    return str(ruta)


@pytest.fixture
def csv_latin1(tmp_path) -> str:
    """CSV con caracteres especiales codificado en latin-1."""
    ruta = tmp_path / "datos_latin.csv"
    df = pd.DataFrame({
        'Equipo': ['Motor_Línea_1', 'Compresor_Señal'],
        'Consumo_kWh': [100.0, 200.0],
        'Horas_Operativas': [20, 22],
        'Fallas_Detectadas': [1, 0]
    })
    df.to_csv(ruta, index=False, encoding='latin-1')
    return str(ruta)


@pytest.fixture
def excel_basico(datos_basicos: pd.DataFrame, tmp_path) -> str:
    """Guarda el dataset básico como Excel temporal."""
    ruta = tmp_path / "datos_test.xlsx"
    datos_basicos.to_excel(ruta, index=False)
    return str(ruta)


# ============================================================================
# TESTS: PROCESAMIENTO DE DATOS
# ============================================================================
class TestProcesarDatos:
    """Tests para la función procesar_datos()."""

    def test_carga_csv_exitosa(self, csv_basico: str) -> None:
        """Verifica que un CSV válido se carga y procesa correctamente."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        assert isinstance(resultado, pd.DataFrame)
        assert len(resultado) == 3  # 3 equipos únicos

    def test_carga_excel_exitosa(self, excel_basico: str) -> None:
        """Verifica que un Excel válido se carga y procesa correctamente."""
        resultado = generar_reporte.procesar_datos(excel_basico)
        assert isinstance(resultado, pd.DataFrame)
        assert len(resultado) == 3

    def test_columnas_generadas(self, csv_basico: str) -> None:
        """Verifica que las columnas de salida son las esperadas."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        columnas_esperadas = [
            'Equipo', 'Consumo Total (kWh)', 'Consumo Promedio (kWh)',
            'Horas Totales', 'Horas Promedio', 'Fallas Totales'
        ]
        assert list(resultado.columns) == columnas_esperadas

    def test_calculo_consumo_total(self, csv_basico: str) -> None:
        """Verifica que el consumo total se calcula correctamente."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        motor_a = resultado[resultado['Equipo'] == 'Motor_A']
        assert motor_a['Consumo Total (kWh)'].values[0] == 250.0  # 100 + 150

    def test_calculo_fallas_totales(self, csv_basico: str) -> None:
        """Verifica que las fallas se suman correctamente."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        compresor = resultado[resultado['Equipo'] == 'Compresor_C']
        assert compresor['Fallas Totales'].values[0] == 4  # 3 + 1

    def test_calculo_promedio(self, csv_basico: str) -> None:
        """Verifica que los promedios se calculan correctamente."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        bomba = resultado[resultado['Equipo'] == 'Bomba_B']
        assert bomba['Consumo Promedio (kWh)'].values[0] == 225.0  # (200+250)/2

    def test_archivo_no_encontrado(self) -> None:
        """Verifica que se lanza FileNotFoundError con archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            generar_reporte.procesar_datos("/ruta/inexistente.csv")

    def test_formato_no_soportado(self, tmp_path) -> None:
        """Verifica que se rechaza un formato de archivo no soportado."""
        ruta = tmp_path / "datos.json"
        ruta.write_text("{}")
        with pytest.raises(ValueError, match="no soportado"):
            generar_reporte.procesar_datos(str(ruta))

    def test_columnas_faltantes(self, tmp_path) -> None:
        """Verifica que se detectan columnas faltantes en el CSV."""
        ruta = tmp_path / "datos_incompletos.csv"
        df = pd.DataFrame({'Equipo': ['A'], 'OtraColumna': [1]})
        df.to_csv(ruta, index=False)
        with pytest.raises(ValueError, match="Columnas faltantes"):
            generar_reporte.procesar_datos(str(ruta))

    def test_valores_redondeados(self, csv_basico: str) -> None:
        """Verifica que los valores numéricos están redondeados a 2 decimales."""
        resultado = generar_reporte.procesar_datos(csv_basico)
        for col in resultado.select_dtypes(include='float').columns:
            for val in resultado[col]:
                # Verificar que no hay más de 2 decimales
                assert round(val, 2) == val


# ============================================================================
# TESTS: GENERACIÓN DE GRÁFICO
# ============================================================================
class TestGenerarGrafico:
    """Tests para la función generar_grafico()."""

    def test_grafico_se_crea(self, csv_basico: str) -> None:
        """Verifica que el gráfico PNG se genera correctamente."""
        df = generar_reporte.procesar_datos(csv_basico)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            ruta = tmp.name
        try:
            generar_reporte.generar_grafico(df, ruta)
            assert os.path.exists(ruta)
            assert os.path.getsize(ruta) > 0
        finally:
            os.remove(ruta)

    def test_grafico_muchos_equipos(self, tmp_path) -> None:
        """Verifica que funciona con más equipos que colores definidos."""
        df = pd.DataFrame({
            'Equipo': [f'Equipo_{i}' for i in range(15)],
            'Consumo Total (kWh)': range(100, 1600, 100)
        })
        ruta = str(tmp_path / "grafico_test.png")
        generar_reporte.generar_grafico(df, ruta)
        assert os.path.exists(ruta)


# ============================================================================
# TESTS: GENERACIÓN DE PDF
# ============================================================================
class TestGenerarPDF:
    """Tests para la función generar_pdf()."""

    def test_pdf_se_crea(self, csv_basico: str, tmp_path) -> None:
        """Verifica que el PDF se genera correctamente."""
        df = generar_reporte.procesar_datos(csv_basico)
        ruta_grafico = str(tmp_path / "grafico.png")
        ruta_pdf = str(tmp_path / "reporte.pdf")

        generar_reporte.generar_grafico(df, ruta_grafico)
        generar_reporte.generar_pdf(df, ruta_grafico, ruta_pdf)

        assert os.path.exists(ruta_pdf)
        assert os.path.getsize(ruta_pdf) > 0

    def test_pdf_sin_grafico(self, csv_basico: str, tmp_path) -> None:
        """Verifica que el PDF se genera incluso si falta el gráfico."""
        df = generar_reporte.procesar_datos(csv_basico)
        ruta_pdf = str(tmp_path / "reporte_sin_grafico.pdf")

        # Usar ruta de gráfico inexistente
        generar_reporte.generar_pdf(df, "/inexistente.png", ruta_pdf)
        assert os.path.exists(ruta_pdf)


# ============================================================================
# TESTS: FLUJO COMPLETO
# ============================================================================
class TestMain:
    """Tests de integración para el flujo main()."""

    def test_flujo_completo_csv(self, csv_basico: str, tmp_path) -> None:
        """Verifica el flujo completo con CSV."""
        ruta_pdf = str(tmp_path / "reporte_final.pdf")
        generar_reporte.main(csv_basico, ruta_pdf)
        assert os.path.exists(ruta_pdf)
        assert os.path.getsize(ruta_pdf) > 1000  # PDF mínimo razonable

    def test_flujo_completo_excel(self, excel_basico: str, tmp_path) -> None:
        """Verifica el flujo completo con Excel."""
        ruta_pdf = str(tmp_path / "reporte_excel.pdf")
        generar_reporte.main(excel_basico, ruta_pdf)
        assert os.path.exists(ruta_pdf)

    def test_no_deja_archivos_temporales(self, csv_basico: str,
                                          tmp_path) -> None:
        """Verifica que main() no crea grafico_consumo.png en el CWD."""
        ruta_pdf = str(tmp_path / "reporte.pdf")
        # Limpiar artefacto antiguo si existe de versiones previas
        legacy_png = os.path.join(os.getcwd(), 'grafico_consumo.png')
        legacy_existed = os.path.exists(legacy_png)
        if legacy_existed:
            os.remove(legacy_png)

        generar_reporte.main(csv_basico, ruta_pdf)

        # main() no debe crear grafico_consumo.png en el CWD
        assert not os.path.exists(legacy_png)
