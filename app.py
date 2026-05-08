"""
Interfaz Gráfica - Generador Automático de Reportes Industriales
=================================================================
Proyecto 1 - Portafolio IIoT

GUI con Tkinter que permite seleccionar archivos de datos y generar
reportes ejecutivos en PDF mediante un flujo de 2 pasos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging

import generar_reporte

# Configurar logging para la GUI
logger = logging.getLogger(__name__)


class AplicacionReportes:
    """Interfaz gráfica para la generación de reportes industriales.

    Flujo de uso:
        1. Seleccionar archivo CSV/Excel con datos de equipos.
        2. Generar y guardar el reporte PDF ejecutivo.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Generador Automático de Reportes Industriales")
        self.root.geometry("550x400")
        self.root.configure(bg="#f4f6f9")
        self.root.resizable(False, False)

        # Estilos de la interfaz
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("TLabel", font=("Helvetica", 11), background="#f4f6f9")
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"),
                         background="#f4f6f9", foreground="#2c3e50")
        style.configure("Success.TLabel", foreground="#27ae60",
                         background="#f4f6f9")
        style.configure("Muted.TLabel", foreground="gray",
                         background="#f4f6f9")

        self.archivo_seleccionado: str | None = None

        self._crear_interfaz()
        logger.info("GUI inicializada correctamente")

    def _crear_interfaz(self) -> None:
        """Construye todos los widgets de la interfaz."""
        # Título
        lbl_titulo = ttk.Label(
            self.root, text="📊 Generador de Reportes Industriales",
            style="Header.TLabel"
        )
        lbl_titulo.pack(pady=(20, 5))

        # Subtítulo
        lbl_subtitulo = ttk.Label(
            self.root,
            text="Convierte datos de equipos en reportes ejecutivos PDF",
            foreground="#7f8c8d"
        )
        lbl_subtitulo.pack(pady=(0, 15))

        # --- Paso 1 ---
        lbl_instrucciones = ttk.Label(
            self.root,
            text="Paso 1: Selecciona el origen de datos (CSV o Excel)"
        )
        lbl_instrucciones.pack(pady=(10, 5))

        btn_seleccionar = ttk.Button(
            self.root, text="📁 Cargar Archivo",
            command=self._seleccionar_archivo
        )
        btn_seleccionar.pack(pady=5)

        self.lbl_ruta = ttk.Label(
            self.root, text="Ningún archivo seleccionado",
            style="Muted.TLabel", wraplength=480, justify="center"
        )
        self.lbl_ruta.pack(pady=(5, 15))

        # Separador visual
        ttk.Separator(self.root, orient='horizontal').pack(
            fill='x', padx=20, pady=10
        )

        # --- Paso 2 ---
        lbl_paso2 = ttk.Label(
            self.root, text="Paso 2: Generar y guardar el reporte final"
        )
        lbl_paso2.pack(pady=(10, 5))

        self.btn_generar = ttk.Button(
            self.root, text="📄 Generar Reporte PDF",
            command=self._generar_reporte, state=tk.DISABLED
        )
        self.btn_generar.pack(pady=5)

        # Barra de estado
        self.lbl_estado = ttk.Label(
            self.root, text="", style="Muted.TLabel"
        )
        self.lbl_estado.pack(pady=(15, 5))

        # Versión
        lbl_version = ttk.Label(
            self.root, text="v2.0 — Portafolio IIoT",
            foreground="#bdc3c7", font=("Helvetica", 9)
        )
        lbl_version.pack(side=tk.BOTTOM, pady=5)

    def _seleccionar_archivo(self) -> None:
        """Abre el diálogo de selección de archivos y valida la extensión."""
        tipos_archivos = [
            ("Archivos soportados", "*.csv *.xlsx *.xls"),
            ("Archivos CSV", "*.csv"),
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Todos los archivos", "*.*")
        ]
        ruta = filedialog.askopenfilename(
            title="Seleccionar datos de origen",
            filetypes=tipos_archivos
        )

        if ruta:
            self.archivo_seleccionado = ruta
            nombre_archivo = os.path.basename(ruta)
            tamano_mb = os.path.getsize(ruta) / (1024 * 1024)
            self.lbl_ruta.config(
                text=f"✅ {nombre_archivo} ({tamano_mb:.1f} MB)",
                style="Success.TLabel"
            )
            self.btn_generar.config(state=tk.NORMAL)
            self.lbl_estado.config(text="Archivo cargado. Listo para generar.")
            logger.info(f"Archivo seleccionado: {nombre_archivo}")

    def _generar_reporte(self) -> None:
        """Ejecuta la generación del reporte PDF con manejo de errores."""
        if not self.archivo_seleccionado:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un archivo primero."
            )
            return

        ruta_guardado = filedialog.asksaveasfilename(
            title="Guardar reporte como",
            defaultextension=".pdf",
            initialfile="Reporte_Ejecutivo.pdf",
            filetypes=[("Archivo PDF", "*.pdf")]
        )

        if ruta_guardado:
            try:
                self.root.config(cursor="watch")
                self.lbl_estado.config(text="⏳ Generando reporte...")
                self.root.update()

                logger.info("Iniciando generación de reporte desde GUI")
                generar_reporte.main(self.archivo_seleccionado, ruta_guardado)

                self.lbl_estado.config(text="✅ Reporte generado exitosamente")
                messagebox.showinfo(
                    "Éxito",
                    f"¡El reporte se ha generado correctamente!\n"
                    f"Guardado en:\n{ruta_guardado}"
                )
                logger.info(f"Reporte guardado en: {ruta_guardado}")
            except FileNotFoundError as e:
                logger.error(f"Archivo no encontrado: {e}")
                self.lbl_estado.config(text="❌ Error: archivo no encontrado")
                messagebox.showerror("Error - Archivo", str(e))
            except ValueError as e:
                logger.error(f"Error de datos: {e}")
                self.lbl_estado.config(text="❌ Error: formato de datos")
                messagebox.showerror("Error - Datos", str(e))
            except Exception as e:
                logger.error(f"Error inesperado: {e}", exc_info=True)
                self.lbl_estado.config(text="❌ Error inesperado")
                messagebox.showerror(
                    "Error",
                    f"Ha ocurrido un error al generar el reporte:\n{str(e)}"
                )
            finally:
                self.root.config(cursor="")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionReportes(root)
    root.mainloop()
