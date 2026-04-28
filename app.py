import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import generar_reporte

class AplicacionReportes:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador Automático de Reportes")
        self.root.geometry("500x350")
        self.root.configure(bg="#f4f6f9")
        
        # Estilos de la interfaz
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("TLabel", font=("Helvetica", 11), background="#f4f6f9")
        
        self.archivo_seleccionado = None
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Título
        lbl_titulo = tk.Label(self.root, text="Generador de Reportes Industriales", font=("Helvetica", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
        lbl_titulo.pack(pady=(20, 10))
        
        # Instrucciones Paso 1
        lbl_instrucciones = ttk.Label(self.root, text="Paso 1: Selecciona el origen de datos (CSV o Excel)")
        lbl_instrucciones.pack(pady=(10, 5))
        
        # Botón para seleccionar archivo
        btn_seleccionar = ttk.Button(self.root, text="Cargar Archivo", command=self.seleccionar_archivo)
        btn_seleccionar.pack(pady=5)
        
        # Etiqueta para mostrar la ruta del archivo
        self.lbl_ruta = ttk.Label(self.root, text="Ningún archivo seleccionado", foreground="gray", wraplength=450, justify="center")
        self.lbl_ruta.pack(pady=(5, 20))
        
        # Separador visual
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # Instrucciones Paso 2
        lbl_paso2 = ttk.Label(self.root, text="Paso 2: Generar y guardar el reporte final")
        lbl_paso2.pack(pady=(10, 5))
        
        # Botón para generar reporte (Inicia deshabilitado hasta que haya archivo)
        self.btn_generar = ttk.Button(self.root, text="Generar Reporte PDF", command=self.generar_reporte, state=tk.DISABLED)
        self.btn_generar.pack(pady=5)
        
    def seleccionar_archivo(self):
        tipos_archivos = [
            ("Archivos soportados", "*.csv *.xlsx *.xls"),
            ("Archivos CSV", "*.csv"),
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Todos los archivos", "*.*")
        ]
        ruta = filedialog.askopenfilename(title="Seleccionar datos de origen", filetypes=tipos_archivos)
        
        if ruta:
            self.archivo_seleccionado = ruta
            nombre_archivo = os.path.basename(ruta)
            self.lbl_ruta.config(text=f"Seleccionado: {nombre_archivo}", foreground="green")
            self.btn_generar.config(state=tk.NORMAL)
            
    def generar_reporte(self):
        if not self.archivo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo primero.")
            return
            
        ruta_guardado = filedialog.asksaveasfilename(
            title="Guardar reporte como",
            defaultextension=".pdf",
            initialfile="Reporte_Ejecutivo.pdf",
            filetypes=[("Archivo PDF", "*.pdf")]
        )
        
        if ruta_guardado:
            try:
                # Cambiar el cursor a "cargando"
                self.root.config(cursor="watch")
                self.root.update()
                
                # Invocar la lógica principal del reporte
                generar_reporte.main(self.archivo_seleccionado, ruta_guardado)
                
                messagebox.showinfo("Éxito", f"¡El reporte se ha generado correctamente!\nGuardado en:\n{ruta_guardado}")
            except Exception as e:
                messagebox.showerror("Error", f"Ha ocurrido un error al generar el reporte:\n{str(e)}")
            finally:
                # Restaurar cursor normal
                self.root.config(cursor="")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionReportes(root)
    root.mainloop()
