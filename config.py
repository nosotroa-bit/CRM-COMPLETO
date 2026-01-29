"""
CONFIG.PY - Configuración del Sistema
Gestión de rutas y parámetros globales
"""

import os
from pathlib import Path

# ============================================================================
# RUTAS DE ONEDRIVE
# ============================================================================

# 🔧 CONFIGURA AQUÍ TU RUTA DE ONEDRIVE
# Ruta configurada manualmente para tu caso
ONEDRIVE_BASE = "C:/Users/ferna/OneDrive"

# Ruta completa a la carpeta de datos
RUTA_DATOS = os.path.join(ONEDRIVE_BASE, "CONSULTORIA GASTRONOMICA", "SISTEMA OPERATIVO", "datos")

# ============================================================================
# RUTAS DE LOS ARCHIVOS EXCEL
# ============================================================================

ARCHIVO_CRM = os.path.join(RUTA_DATOS, "CRM_CLIENTES.xlsx")
ARCHIVO_OPERACIONES = os.path.join(RUTA_DATOS, "OPERACIONES_ESCANDALLOS.xlsx")
ARCHIVO_PROVEEDORES = os.path.join(RUTA_DATOS, "PROVEEDORES_MERCADO.xlsx")
ARCHIVO_EMPRESA = os.path.join(RUTA_DATOS, "EMPRESA_BACKOFFICE.xlsx")

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

# Nombre de la empresa
NOMBRE_EMPRESA = "Consultoría HORECA"

# Colores corporativos (para gráficos)
COLOR_PRIMARIO = "#366092"
COLOR_SECUNDARIO = "#5B9BD5"
COLOR_EXITO = "#70AD47"
COLOR_ADVERTENCIA = "#FFC000"
COLOR_PELIGRO = "#FF0000"

# Umbrales de alerta
UMBRAL_MARGEN_MINIMO = 20  # % mínimo de margen en platos
UMBRAL_FOOD_COST_MAXIMO = 35  # % máximo de food cost
UMBRAL_DESVIACION_PRECIO = 15  # % de desviación precio vs mercado para alertar

# Opciones de menús desplegables
TIPOS_LOCAL = ["Bar", "Restaurante", "Cafetería", "Gastrobar", "Taberna", "Asador"]
ESTADOS_LEAD = ["Prospecto", "Contactado", "Diagnóstico", "Propuesta Enviada", "Cliente", "Perdido", "Baja"]
FUENTES_CAPTACION = ["Puerta Fría", "Referido", "Web", "RRSS", "Evento", "Llamada"]
PRIORIDADES = ["Alta", "Media", "Baja"]
SERVICIOS = ["Básico", "Premium", "Cuota Mensual"]
CATEGORIAS_PLATO = ["Entrante", "Principal", "Postre", "Bebida", "Tapa", "Menú"]
CATEGORIAS_INGREDIENTE = ["Carne", "Pescado", "Verdura", "Lácteo", "Aceite", "Especias", "Otros"]
TIPOS_PROVEEDOR = ["Mayorista", "Distribuidor", "Productor", "Cash&Carry"]

# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def verificar_archivos_excel():
    """Verifica que todos los archivos Excel existen"""
    archivos = [
        ("CRM", ARCHIVO_CRM),
        ("Operaciones", ARCHIVO_OPERACIONES),
        ("Proveedores", ARCHIVO_PROVEEDORES),
        ("Empresa", ARCHIVO_EMPRESA)
    ]
    
    archivos_faltantes = []
    for nombre, ruta in archivos:
        if not os.path.exists(ruta):
            archivos_faltantes.append(f"{nombre}: {ruta}")
    
    return archivos_faltantes

def crear_carpetas_si_no_existen():
    """Crea las carpetas necesarias si no existen"""
    Path(RUTA_DATOS).mkdir(parents=True, exist_ok=True)
    
    # Carpeta para documentos
    carpeta_docs = os.path.join(ONEDRIVE_BASE, "CONSULTORIA_HORECA", "documentos")
    Path(carpeta_docs).mkdir(parents=True, exist_ok=True)
    
    return True

# ============================================================================
# MENSAJES DE AYUDA
# ============================================================================

MENSAJE_PRIMERA_VEZ = """
## 🎉 ¡Bienvenido al Sistema de Gestión HORECA!

### 📋 Pasos para empezar:

1. **Asegúrate de tener los 4 archivos Excel en OneDrive:**
   - CRM_CLIENTES.xlsx
   - OPERACIONES_ESCANDALLOS.xlsx
   - PROVEEDORES_MERCADO.xlsx
   - EMPRESA_BACKOFFICE.xlsx

2. **Ruta esperada:**
   ```
   {ruta}
   ```

3. **Si los archivos no están ahí:**
   - Crea la carpeta manualmente
   - Copia los 4 archivos Excel
   - Reinicia esta aplicación

4. **¡Listo para empezar!**
"""

if __name__ == "__main__":
    print("🔧 Configuración del Sistema")
    print("="*60)
    print(f"📁 Ruta OneDrive: {ONEDRIVE_BASE}")
    print(f"📁 Ruta Datos: {RUTA_DATOS}")
    print("="*60)
    
    crear_carpetas_si_no_existen()
    archivos_faltantes = verificar_archivos_excel()
    
    if archivos_faltantes:
        print("\n⚠️  ARCHIVOS FALTANTES:")
        for archivo in archivos_faltantes:
            print(f"   ❌ {archivo}")
    else:
        print("\n✅ Todos los archivos Excel encontrados correctamente")
