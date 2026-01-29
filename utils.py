"""
UTILS.PY - Funciones Utilitarias
Lectura/Escritura de Excel y funciones comunes
"""

import pandas as pd
import streamlit as st
from datetime import datetime, date
import config

# ============================================================================
# FUNCIONES DE LECTURA DE EXCEL
# ============================================================================

def leer_excel(archivo, hoja):
    """
    Lee una hoja de Excel y la devuelve como DataFrame
    
    Args:
        archivo: Ruta del archivo Excel
        hoja: Nombre de la hoja a leer
    
    Returns:
        DataFrame con los datos
    """
    try:
        df = pd.read_excel(archivo, sheet_name=hoja)
        return df
    except Exception as e:
        st.error(f"Error al leer {archivo} - {hoja}: {str(e)}")
        return pd.DataFrame()

def leer_todas_hojas(archivo):
    """Lee todas las hojas de un archivo Excel"""
    try:
        excel_file = pd.ExcelFile(archivo)
        hojas = {}
        for nombre_hoja in excel_file.sheet_names:
            hojas[nombre_hoja] = pd.read_excel(archivo, sheet_name=nombre_hoja)
        return hojas
    except Exception as e:
        st.error(f"Error al leer {archivo}: {str(e)}")
        return {}

# ============================================================================
# FUNCIONES DE ESCRITURA EN EXCEL
# ============================================================================

def escribir_excel(archivo, hoja, df):
    """
    Escribe un DataFrame en una hoja específica de Excel
    Preserva las otras hojas del archivo
    
    Args:
        archivo: Ruta del archivo Excel
        hoja: Nombre de la hoja a escribir
        df: DataFrame a escribir
    """
    try:
        # Leer todas las hojas existentes
        excel_file = pd.ExcelFile(archivo)
        hojas_existentes = {}
        
        for nombre_hoja in excel_file.sheet_names:
            if nombre_hoja == hoja:
                # Usar el DataFrame nuevo para esta hoja
                hojas_existentes[nombre_hoja] = df
            else:
                # Mantener las otras hojas como están
                hojas_existentes[nombre_hoja] = pd.read_excel(archivo, sheet_name=nombre_hoja)
        
        # Si la hoja no existía, agregarla
        if hoja not in hojas_existentes:
            hojas_existentes[hoja] = df
        
        # Escribir todo de vuelta
        with pd.ExcelWriter(archivo, engine='openpyxl', mode='w') as writer:
            for nombre_hoja, datos in hojas_existentes.items():
                datos.to_excel(writer, sheet_name=nombre_hoja, index=False)
        
        print(f"[DEBUG] ✅ Excel guardado: {hoja} con {len(df)} filas")
        return True
        
    except PermissionError as e:
        st.error(f"❌ El archivo está bloqueado. Cierra Excel y OneDrive debe terminar de sincronizar.")
        print(f"[DEBUG] ❌ PermissionError: {e}")
        return False
        
    except Exception as e:
        st.error(f"Error al escribir en {archivo}: {str(e)}")
        print(f"[DEBUG] ❌ Error escribiendo: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def agregar_fila(archivo, hoja, nueva_fila):
    """
    Agrega una nueva fila a una hoja de Excel
    
    Args:
        archivo: Ruta del archivo
        hoja: Nombre de la hoja
        nueva_fila: Dict con los datos de la nueva fila
    """
    try:
        # Leer la hoja actual directamente
        df = pd.read_excel(archivo, sheet_name=hoja)
        
        print(f"[DEBUG] Agregando fila a {hoja}")
        print(f"[DEBUG] Nombre: {nueva_fila.get('Nombre Comercial', nueva_fila.get('Nombre', 'N/A'))}")
        print(f"[DEBUG] Filas antes: {len(df)}")
        
        # Agregar la nueva fila
        nuevo_df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        
        print(f"[DEBUG] Filas después: {len(nuevo_df)}")
        
        # Escribir de vuelta
        resultado = escribir_excel(archivo, hoja, nuevo_df)
        
        if resultado:
            print(f"[DEBUG] ✅ Fila agregada y guardada en {hoja}")
            
            # Verificar que se guardó
            df_verif = pd.read_excel(archivo, sheet_name=hoja)
            print(f"[DEBUG] Verificación: ahora hay {len(df_verif)} filas en {hoja}")
        else:
            print(f"[DEBUG] ❌ Error al guardar en {hoja}")
            
        return resultado
        
    except Exception as e:
        print(f"[DEBUG] ❌ Excepción al agregar fila: {str(e)}")
        st.error(f"Error al agregar fila: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def actualizar_fila(archivo, hoja, indice, columna, nuevo_valor):
    """
    Actualiza un valor específico en una fila
    
    Args:
        archivo: Ruta del archivo
        hoja: Nombre de la hoja
        indice: Índice de la fila (número de ID típicamente)
        columna: Nombre de la columna a actualizar
        nuevo_valor: Nuevo valor
    """
    try:
        df = leer_excel(archivo, hoja)
        df.loc[df.iloc[:, 0] == indice, columna] = nuevo_valor
        return escribir_excel(archivo, hoja, df)
    except Exception as e:
        st.error(f"Error al actualizar: {str(e)}")
        return False

def eliminar_fila(archivo, hoja, indice):
    """
    Elimina una fila basándose en el ID (primera columna)
    
    Args:
        archivo: Ruta del archivo
        hoja: Nombre de la hoja
        indice: ID de la fila a eliminar
    """
    try:
        df = leer_excel(archivo, hoja)
        df = df[df.iloc[:, 0] != indice]
        return escribir_excel(archivo, hoja, df)
    except Exception as e:
        st.error(f"Error al eliminar: {str(e)}")
        return False

# ============================================================================
# FUNCIONES DE CÁLCULO Y RETROALIMENTACIÓN
# ============================================================================

def actualizar_precio_mercado(id_ingrediente, nuevo_precio):
    """
    Actualiza el precio de mercado de un ingrediente
    y recalcula los escandallos afectados
    """
    try:
        # 1. Actualizar precio en INGREDIENTES_MAESTRO
        df_ing = leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        df_ing.loc[df_ing['ID Ingrediente'] == id_ingrediente, 'Precio Mercado Medio'] = nuevo_precio
        df_ing.loc[df_ing['ID Ingrediente'] == id_ingrediente, 'Última Actualización'] = datetime.now()
        escribir_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO", df_ing)
        
        # 2. Actualizar escandallos que usan ese ingrediente
        df_esc = leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
        mascara = df_esc['ID Ingrediente'] == id_ingrediente
        df_esc.loc[mascara, 'Coste Unitario'] = nuevo_precio
        df_esc.loc[mascara, 'Última Actualización'] = datetime.now()
        escribir_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", df_esc)
        
        # 3. Recalcular costes de platos afectados
        recalcular_costes_platos(df_esc)
        
        return True
    except Exception as e:
        st.error(f"Error al actualizar precio: {str(e)}")
        return False

def recalcular_costes_platos(df_escandallos):
    """
    Recalcula el coste total de todos los platos
    basándose en sus escandallos
    """
    try:
        # Agrupar por plato y sumar costes
        costes_por_plato = df_escandallos.groupby('ID Plato').agg({
            'Coste Total': 'sum'
        }).reset_index()
        
        # Actualizar en CARTA_CLIENTES
        df_carta = leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
        
        for _, row in costes_por_plato.iterrows():
            id_plato = row['ID Plato']
            nuevo_coste = row['Coste Total']
            
            mascara = df_carta['ID Plato'] == id_plato
            df_carta.loc[mascara, 'Coste Total'] = nuevo_coste
            
            # Recalcular márgenes
            precio_venta = df_carta.loc[mascara, 'Precio Venta'].values[0]
            if precio_venta > 0:
                margen_euros = precio_venta - nuevo_coste
                margen_pct = (margen_euros / precio_venta) * 100
                food_cost = (nuevo_coste / precio_venta) * 100
                
                df_carta.loc[mascara, 'Margen €'] = margen_euros
                df_carta.loc[mascara, 'Margen %'] = margen_pct
                df_carta.loc[mascara, 'Food Cost %'] = food_cost
        
        escribir_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", df_carta)
        return True
    except Exception as e:
        st.error(f"Error al recalcular costes: {str(e)}")
        return False

def detectar_alertas_precios():
    """
    Detecta si hay ingredientes comprados muy por encima del precio de mercado
    Retorna lista de alertas
    """
    alertas = []
    
    try:
        df_lineas = leer_excel(config.ARCHIVO_OPERACIONES, "LINEAS_COMPRA")
        df_ingredientes = leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        
        for _, linea in df_lineas.iterrows():
            id_ing = linea['ID Ingrediente']
            precio_pagado = linea['Precio Unitario']
            
            # Buscar precio de mercado
            ing = df_ingredientes[df_ingredientes['ID Ingrediente'] == id_ing]
            if not ing.empty:
                precio_mercado = ing['Precio Mercado Medio'].values[0]
                
                if precio_mercado > 0:
                    desviacion = ((precio_pagado - precio_mercado) / precio_mercado) * 100
                    
                    if desviacion > config.UMBRAL_DESVIACION_PRECIO:
                        alertas.append({
                            'tipo': 'PRECIO_ALTO',
                            'ingrediente': linea['Nombre Ingrediente'],
                            'precio_pagado': precio_pagado,
                            'precio_mercado': precio_mercado,
                            'desviacion': round(desviacion, 1),
                            'ahorro_potencial': (precio_pagado - precio_mercado) * linea['Cantidad']
                        })
        
        return alertas
    except Exception as e:
        st.error(f"Error al detectar alertas: {str(e)}")
        return []

def detectar_alertas_margenes():
    """
    Detecta platos con márgenes peligrosamente bajos
    """
    alertas = []
    
    try:
        df_carta = leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
        
        for _, plato in df_carta.iterrows():
            if plato['Activo'] == 'Sí':
                margen = plato['Margen %']
                
                if margen < config.UMBRAL_MARGEN_MINIMO:
                    alertas.append({
                        'tipo': 'MARGEN_BAJO',
                        'cliente': plato['Nombre Cliente'],
                        'plato': plato['Nombre Plato'],
                        'margen_actual': round(margen, 1),
                        'precio_venta': plato['Precio Venta'],
                        'coste': plato['Coste Total']
                    })
        
        return alertas
    except Exception as e:
        st.error(f"Error al detectar alertas de margen: {str(e)}")
        return []

# ============================================================================
# FUNCIONES DE FORMATEO
# ============================================================================

def formatear_moneda(valor):
    """Formatea un número como moneda"""
    try:
        return f"{float(valor):,.2f} €"
    except:
        return "0,00 €"

def formatear_porcentaje(valor):
    """Formatea un número como porcentaje"""
    try:
        return f"{float(valor):.1f}%"
    except:
        return "0.0%"

def color_margen(margen):
    """Devuelve color según el margen"""
    try:
        margen = float(margen)
        if margen < 20:
            return 'red'
        elif margen < 30:
            return 'orange'
        else:
            return 'green'
    except:
        return 'black'

# ============================================================================
# FUNCIONES DE ID AUTOMÁTICO
# ============================================================================

def obtener_siguiente_id(archivo, hoja):
    """
    Obtiene el siguiente ID disponible en una hoja
    Asume que la primera columna es el ID
    """
    try:
        df = leer_excel(archivo, hoja)
        if df.empty:
            return 1
        
        max_id = df.iloc[:, 0].max()
        return int(max_id) + 1 if pd.notna(max_id) else 1
    except:
        return 1

# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validar_email(email):
    """Valida formato de email"""
    import re
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    """Valida formato de teléfono español"""
    import re
    patron = r'^[6-9]\d{8}$'
    telefono_limpio = ''.join(filter(str.isdigit, str(telefono)))
    return re.match(patron, telefono_limpio) is not None

def validar_cif(cif):
    """Valida formato de CIF español (básico)"""
    import re
    patron = r'^[A-Z]\d{8}$'
    return re.match(patron, str(cif).upper()) is not None

# ============================================================================
# FUNCIONES DE FECHA
# ============================================================================

def fecha_a_texto(fecha):
    """Convierte fecha a texto legible"""
    if pd.isna(fecha):
        return ""
    try:
        if isinstance(fecha, str):
            return fecha
        return fecha.strftime("%d/%m/%Y")
    except:
        return ""

def texto_a_fecha(texto):
    """Convierte texto a fecha"""
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except:
        return None
