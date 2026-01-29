"""
MAIN.PY - Aplicación Principal
Sistema de Gestión Integral - Consultoría HORECA
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import config
import utils

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Consultoría HORECA - Sistema de Gestión",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #366092;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #366092;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# VERIFICACIÓN DE ARCHIVOS
# ============================================================================

def verificar_sistema():
    """Verifica que todo esté correctamente configurado"""
    archivos_faltantes = config.verificar_archivos_excel()
    
    if archivos_faltantes:
        st.error("⚠️ Archivos Excel no encontrados")
        st.markdown(config.MENSAJE_PRIMERA_VEZ.format(ruta=config.RUTA_DATOS))
        for archivo in archivos_faltantes:
            st.write(f"❌ {archivo}")
        st.stop()
    
    return True

# ============================================================================
# SIDEBAR - NAVEGACIÓN
# ============================================================================

def mostrar_sidebar():
    """Renderiza el menú lateral"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/366092/FFFFFF?text=HORECA", 
                 use_container_width=True)
        
        st.markdown("---")
        
        # Selector de módulo
        modulo = st.radio(
            "📋 MÓDULOS",
            [
                "🏠 Dashboard",
                "👥 CRM - Clientes",
                "🍽️ Escandallos",
                "🏢 Proveedores",
                "💼 Empresa",
                "⚙️ Configuración"
            ],
            label_visibility="visible"
        )
        
        st.markdown("---")
        
        # Información del sistema
        st.caption(f"**Sistema:** {config.NOMBRE_EMPRESA}")
        st.caption(f"**Versión:** 1.0.0")
        st.caption(f"**Última sync:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Botón de refresco
        if st.button("🔄 Refrescar Datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    return modulo

# ============================================================================
# MÓDULO: DASHBOARD
# ============================================================================

def modulo_dashboard():
    """Dashboard principal con resumen ejecutivo"""
    st.markdown('<h1 class="main-header">🏠 Dashboard Ejecutivo</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    df_servicios = utils.leer_excel(config.ARCHIVO_CRM, "SERVICIOS")
    df_kpis = utils.leer_excel(config.ARCHIVO_EMPRESA, "KPIS_MENSUALES")
    
    # Fila 1: Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(df_leads)
        st.metric("📊 Total Leads", total_leads)
    
    with col2:
        clientes_activos = len(df_clientes)
        st.metric("✅ Clientes Activos", clientes_activos)
    
    with col3:
        if not df_clientes.empty and 'MRR' in df_clientes.columns:
            mrr_total = df_clientes['MRR'].sum()
            st.metric("💰 MRR Total", utils.formatear_moneda(mrr_total))
        else:
            st.metric("💰 MRR Total", "0,00 €")
    
    with col4:
        if total_leads > 0 and clientes_activos > 0:
            tasa_conv = (clientes_activos / total_leads) * 100
            st.metric("📈 Tasa Conversión", f"{tasa_conv:.1f}%")
        else:
            st.metric("📈 Tasa Conversión", "0.0%")
    
    st.markdown("---")
    
    # Fila 2: Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribución de Leads por Estado")
        if not df_leads.empty and 'Estado Lead' in df_leads.columns:
            estados = df_leads['Estado Lead'].value_counts()
            st.bar_chart(estados)
        else:
            st.info("No hay datos de leads todavía")
    
    with col2:
        st.subheader("💼 Servicios Este Mes")
        if not df_servicios.empty:
            mes_actual = datetime.now().month
            servicios_mes = df_servicios[pd.to_datetime(df_servicios['Fecha Solicitud']).dt.month == mes_actual]
            if not servicios_mes.empty:
                tipos_servicio = servicios_mes['Tipo Servicio'].value_counts()
                st.bar_chart(tipos_servicio)
            else:
                st.info("No hay servicios este mes")
        else:
            st.info("No hay datos de servicios")
    
    st.markdown("---")
    
    # Fila 3: Próximas Acciones Pendientes
    st.subheader("📅 Próximas Acciones Pendientes")
    
    # Cargar leads e interacciones
    df_leads_acciones = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    df_interacciones_acciones = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
    
    acciones_pendientes = []
    hoy = datetime.now().date()
    
    # Procesar acciones de LEADS
    if not df_leads_acciones.empty and 'Fecha Próxima Acción' in df_leads_acciones.columns:
        for _, row in df_leads_acciones.iterrows():
            if pd.notna(row.get('Fecha Próxima Acción')) and pd.notna(row.get('Próxima Acción')):
                try:
                    fecha_accion = pd.to_datetime(row['Fecha Próxima Acción']).date()
                    dias_diff = (fecha_accion - hoy).days
                    
                    acciones_pendientes.append({
                        'Fecha': fecha_accion,
                        'Días': dias_diff,
                        'Cliente': row.get('Nombre Comercial', 'N/A'),
                        'Acción': row.get('Próxima Acción', 'N/A'),
                        'Responsable': row.get('Comercial Asignado', 'N/A'),
                        'Origen': 'Lead',
                        'Prioridad': row.get('Prioridad', 'Media')
                    })
                except:
                    pass
    
    # Procesar acciones de INTERACCIONES
    if not df_interacciones_acciones.empty and 'Fecha Próxima Acción' in df_interacciones_acciones.columns:
        for _, row in df_interacciones_acciones.iterrows():
            if pd.notna(row.get('Fecha Próxima Acción')) and pd.notna(row.get('Próxima Acción')):
                try:
                    fecha_accion = pd.to_datetime(row['Fecha Próxima Acción']).date()
                    dias_diff = (fecha_accion - hoy).days
                    
                    acciones_pendientes.append({
                        'Fecha': fecha_accion,
                        'Días': dias_diff,
                        'Cliente': row.get('Nombre Cliente', 'N/A'),
                        'Acción': row.get('Próxima Acción', 'N/A'),
                        'Responsable': row.get('Responsable', 'N/A'),
                        'Origen': 'Interacción',
                        'Prioridad': 'Media'
                    })
                except:
                    pass
    
    if acciones_pendientes:
        # Ordenar por fecha
        acciones_pendientes.sort(key=lambda x: x['Fecha'])
        
        # Separar por urgencia
        vencidas = [a for a in acciones_pendientes if a['Días'] < 0]
        hoy_acciones = [a for a in acciones_pendientes if a['Días'] == 0]
        proximas = [a for a in acciones_pendientes if 0 < a['Días'] <= 7]
        futuras = [a for a in acciones_pendientes if a['Días'] > 7]
        
        # Métricas de acciones
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if vencidas:
                st.metric("🔴 Vencidas", len(vencidas), delta=f"-{len(vencidas)}", delta_color="inverse")
            else:
                st.metric("🔴 Vencidas", 0)
        
        with col2:
            if hoy_acciones:
                st.metric("🟡 Hoy", len(hoy_acciones))
            else:
                st.metric("🟡 Hoy", 0)
        
        with col3:
            if proximas:
                st.metric("🟢 Próximos 7 días", len(proximas))
            else:
                st.metric("🟢 Próximos 7 días", 0)
        
        with col4:
            st.metric("📅 Total Pendientes", len(acciones_pendientes))
        
        st.markdown("---")
        
        # Mostrar acciones vencidas
        if vencidas:
            with st.expander(f"🔴 ACCIONES VENCIDAS ({len(vencidas)})", expanded=True):
                for accion in vencidas[:5]:  # Mostrar máximo 5
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="danger-box">
                            <strong>{accion['Cliente']}</strong><br>
                            📌 {accion['Acción']}<br>
                            📅 Fecha: {accion['Fecha'].strftime('%d/%m/%Y')} <span style="color: red;">({abs(accion['Días'])} días de retraso)</span><br>
                            👤 {accion['Responsable']} | 📍 {accion['Origen']}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write("")
        
        # Mostrar acciones de hoy
        if hoy_acciones:
            with st.expander(f"🟡 ACCIONES PARA HOY ({len(hoy_acciones)})", expanded=True):
                for accion in hoy_acciones:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>{accion['Cliente']}</strong><br>
                            📌 {accion['Acción']}<br>
                            👤 {accion['Responsable']} | 📍 {accion['Origen']}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write("")
        
        # Mostrar acciones próximas
        if proximas:
            with st.expander(f"🟢 PRÓXIMOS 7 DÍAS ({len(proximas)})", expanded=False):
                for accion in proximas:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>{accion['Cliente']}</strong> - 📅 {accion['Fecha'].strftime('%d/%m/%Y')} (en {accion['Días']} días)<br>
                        📌 {accion['Acción']}<br>
                        👤 {accion['Responsable']} | 📍 {accion['Origen']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Mostrar acciones futuras (resumido)
        if futuras:
            with st.expander(f"📅 ACCIONES FUTURAS ({len(futuras)})", expanded=False):
                for accion in futuras[:10]:  # Mostrar máximo 10
                    st.write(f"**{accion['Fecha'].strftime('%d/%m/%Y')}** - {accion['Cliente']}: {accion['Acción']}")
    else:
        st.info("✅ No hay acciones pendientes programadas")
    
    st.markdown("---")
    
    # Fila 4: Alertas del sistema
    st.subheader("🚨 Alertas del Sistema")
    
    alertas_precio = utils.detectar_alertas_precios()
    alertas_margen = utils.detectar_alertas_margenes()
    
    if alertas_precio or alertas_margen:
        col1, col2 = st.columns(2)
        
        with col1:
            if alertas_precio:
                st.warning(f"⚠️ {len(alertas_precio)} alertas de precios altos")
                with st.expander("Ver detalles"):
                    for alerta in alertas_precio[:5]:  # Mostrar solo las 5 primeras
                        st.write(f"**{alerta['ingrediente']}**")
                        st.write(f"- Precio pagado: {utils.formatear_moneda(alerta['precio_pagado'])}")
                        st.write(f"- Precio mercado: {utils.formatear_moneda(alerta['precio_mercado'])}")
                        st.write(f"- Desviación: {alerta['desviacion']}%")
                        st.write(f"- Ahorro potencial: {utils.formatear_moneda(alerta['ahorro_potencial'])}")
                        st.markdown("---")
        
        with col2:
            if alertas_margen:
                st.error(f"❌ {len(alertas_margen)} platos con margen bajo")
                with st.expander("Ver detalles"):
                    for alerta in alertas_margen[:5]:
                        st.write(f"**{alerta['plato']}** ({alerta['cliente']})")
                        st.write(f"- Margen actual: {alerta['margen_actual']}%")
                        st.write(f"- Precio venta: {utils.formatear_moneda(alerta['precio_venta'])}")
                        st.write(f"- Coste: {utils.formatear_moneda(alerta['coste'])}")
                        st.markdown("---")
    else:
        st.success("✅ No hay alertas críticas en este momento")

# ============================================================================
# MÓDULO: CRM
# ============================================================================

def modulo_crm():
    """Módulo de gestión de clientes y leads"""
    st.markdown('<h1 class="main-header">👥 CRM - Gestión de Clientes</h1>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Leads", "✅ Clientes Activos", "📅 Próximas Acciones", "📞 Interacciones", "💼 Servicios"])
    
    with tab1:
        mostrar_leads()
    
    with tab2:
        mostrar_clientes_activos()
    
    with tab3:
        mostrar_proximas_acciones()
    
    with tab4:
        mostrar_interacciones()
    
    with tab5:
        mostrar_servicios()

def mostrar_proximas_acciones():
    """Vista dedicada de próximas acciones con gestión"""
    st.subheader("📅 Agenda de Próximas Acciones")
    
    # Cargar datos
    df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    df_interacciones = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
    
    # Compilar todas las acciones
    acciones = []
    hoy = datetime.now().date()
    
    # Acciones de LEADS
    if not df_leads.empty and 'Fecha Próxima Acción' in df_leads.columns:
        for idx, row in df_leads.iterrows():
            if pd.notna(row.get('Fecha Próxima Acción')) and pd.notna(row.get('Próxima Acción')):
                try:
                    fecha_accion = pd.to_datetime(row['Fecha Próxima Acción']).date()
                    dias_diff = (fecha_accion - hoy).days
                    
                    # Determinar estado
                    if dias_diff < 0:
                        estado = "🔴 Vencida"
                        urgencia = 1
                    elif dias_diff == 0:
                        estado = "🟡 Hoy"
                        urgencia = 2
                    elif dias_diff <= 7:
                        estado = "🟢 Próxima"
                        urgencia = 3
                    else:
                        estado = "📅 Futura"
                        urgencia = 4
                    
                    acciones.append({
                        'Estado': estado,
                        'Urgencia': urgencia,
                        'Fecha': fecha_accion,
                        'Días Restantes': dias_diff,
                        'Cliente/Lead': row.get('Nombre Comercial', 'N/A'),
                        'Acción': row.get('Próxima Acción', 'N/A'),
                        'Responsable': row.get('Comercial Asignado', 'N/A'),
                        'Prioridad': row.get('Prioridad', 'Media'),
                        'Origen': 'Lead',
                        'ID': row.get('ID', '')
                    })
                except:
                    pass
    
    # Acciones de INTERACCIONES
    if not df_interacciones.empty and 'Fecha Próxima Acción' in df_interacciones.columns:
        for idx, row in df_interacciones.iterrows():
            if pd.notna(row.get('Fecha Próxima Acción')) and pd.notna(row.get('Próxima Acción')):
                try:
                    fecha_accion = pd.to_datetime(row['Fecha Próxima Acción']).date()
                    dias_diff = (fecha_accion - hoy).days
                    
                    if dias_diff < 0:
                        estado = "🔴 Vencida"
                        urgencia = 1
                    elif dias_diff == 0:
                        estado = "🟡 Hoy"
                        urgencia = 2
                    elif dias_diff <= 7:
                        estado = "🟢 Próxima"
                        urgencia = 3
                    else:
                        estado = "📅 Futura"
                        urgencia = 4
                    
                    acciones.append({
                        'Estado': estado,
                        'Urgencia': urgencia,
                        'Fecha': fecha_accion,
                        'Días Restantes': dias_diff,
                        'Cliente/Lead': row.get('Nombre Cliente', 'N/A'),
                        'Acción': row.get('Próxima Acción', 'N/A'),
                        'Responsable': row.get('Responsable', 'N/A'),
                        'Prioridad': 'Media',
                        'Origen': 'Interacción',
                        'ID': row.get('ID Interacción', '')
                    })
                except:
                    pass
    
    if acciones:
        # Convertir a DataFrame
        df_acciones = pd.DataFrame(acciones)
        
        # Ordenar por urgencia y luego por fecha
        df_acciones = df_acciones.sort_values(['Urgencia', 'Fecha'])
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_estado = st.multiselect("Filtrar por Estado", 
                df_acciones['Estado'].unique(),
                default=[s for s in df_acciones['Estado'].unique() if s in ["🔴 Vencida", "🟡 Hoy"]])
        
        with col2:
            filtro_responsable = st.multiselect("Filtrar por Responsable", 
                df_acciones['Responsable'].unique())
        
        with col3:
            filtro_origen = st.multiselect("Filtrar por Origen", 
                df_acciones['Origen'].unique())
        
        with col4:
            buscar = st.text_input("🔍 Buscar cliente", key="buscar_proximas_acciones")
        
        # Aplicar filtros
        df_filtrado = df_acciones.copy()
        
        if filtro_estado:
            df_filtrado = df_filtrado[df_filtrado['Estado'].isin(filtro_estado)]
        
        if filtro_responsable:
            df_filtrado = df_filtrado[df_filtrado['Responsable'].isin(filtro_responsable)]
        
        if filtro_origen:
            df_filtrado = df_filtrado[df_filtrado['Origen'].isin(filtro_origen)]
        
        if buscar:
            df_filtrado = df_filtrado[df_filtrado['Cliente/Lead'].str.contains(buscar, case=False, na=False)]
        
        st.markdown("---")
        
        # Resumen de acciones
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            vencidas = len(df_filtrado[df_filtrado['Estado'] == '🔴 Vencida'])
            st.metric("🔴 Vencidas", vencidas)
        
        with col2:
            hoy_count = len(df_filtrado[df_filtrado['Estado'] == '🟡 Hoy'])
            st.metric("🟡 Hoy", hoy_count)
        
        with col3:
            proximas = len(df_filtrado[df_filtrado['Estado'] == '🟢 Próxima'])
            st.metric("🟢 Próximas", proximas)
        
        with col4:
            futuras = len(df_filtrado[df_filtrado['Estado'] == '📅 Futura'])
            st.metric("📅 Futuras", futuras)
        
        with col5:
            st.metric("📊 Total", len(df_filtrado))
        
        st.markdown("---")
        
        # Vista de calendario (simplificada)
        vista = st.radio("Vista:", ["📋 Lista", "📅 Calendario Semanal"], horizontal=True)
        
        if vista == "📋 Lista":
            # Mostrar tabla
            st.dataframe(
                df_filtrado[['Estado', 'Fecha', 'Días Restantes', 'Cliente/Lead', 'Acción', 'Responsable', 'Prioridad', 'Origen']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fecha": st.column_config.DateColumn(
                        "Fecha",
                        format="DD/MM/YYYY"
                    ),
                    "Días Restantes": st.column_config.NumberColumn(
                        "Días",
                        help="Días hasta la acción (negativo = vencida)"
                    )
                }
            )
        
        else:  # Vista Calendario Semanal
            st.write("**📅 Calendario de esta semana**")
            
            # Generar los próximos 7 días
            for i in range(7):
                dia = hoy + pd.Timedelta(days=i)
                acciones_dia = df_filtrado[df_filtrado['Fecha'] == dia]
                
                # Determinar emoji del día
                if i == 0:
                    emoji_dia = "🟡"
                    nombre_dia = "HOY"
                elif i == 1:
                    emoji_dia = "📅"
                    nombre_dia = "MAÑANA"
                else:
                    emoji_dia = "📅"
                    nombre_dia = dia.strftime('%A').upper()
                
                # Mostrar día
                with st.expander(f"{emoji_dia} {nombre_dia} - {dia.strftime('%d/%m/%Y')} ({len(acciones_dia)} acciones)", 
                               expanded=(i < 2)):  # Expandir hoy y mañana
                    if not acciones_dia.empty:
                        for _, accion in acciones_dia.iterrows():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                prioridad_emoji = "🔴" if accion['Prioridad'] == 'Alta' else "🟡" if accion['Prioridad'] == 'Media' else "🟢"
                                st.write(f"{prioridad_emoji} **{accion['Cliente/Lead']}**")
                                st.write(f"   📌 {accion['Acción']}")
                                st.write(f"   👤 {accion['Responsable']} | 📍 {accion['Origen']}")
                            with col2:
                                st.write("")
                                st.caption(f"ID: {accion['ID']}")
                            st.markdown("---")
                    else:
                        st.info("No hay acciones programadas")
        
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_acciones)} acciones")
    
    else:
        st.success("✅ ¡No hay acciones pendientes! Perfecto para tomarse un descanso ☕")
        st.info("Las acciones aparecerán aquí cuando agregues 'Próxima Acción' en Leads o Interacciones")

def convertir_lead_a_cliente(id_lead, df_leads):
    """
    Convierte un lead a cliente activo automáticamente
    
    Args:
        id_lead: ID del lead a convertir
        df_leads: DataFrame de leads
    
    Returns:
        tuple: (bool éxito, str mensaje)
    """
    try:
        # Buscar el lead
        lead = df_leads[df_leads['ID'] == id_lead]
        
        if lead.empty:
            return False, f"Lead #{id_lead} no encontrado"
        
        lead_data = lead.iloc[0]
        nombre_lead = lead_data.get('Nombre Comercial', 'Sin nombre')
        
        # Verificar si ya existe en clientes activos
        df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
        
        # Comprobar si ya existe por nombre comercial
        if not df_clientes.empty and 'Nombre Comercial' in df_clientes.columns:
            existe = df_clientes[df_clientes['Nombre Comercial'] == nombre_lead]
            if not existe.empty:
                # Ya existe, no duplicar
                return True, f"'{nombre_lead}' ya existe como cliente activo"
        
        # Obtener siguiente ID para cliente
        nuevo_id_cliente = utils.obtener_siguiente_id(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
        
        # Crear registro de cliente - usar exactamente los nombres de columnas del Excel
        nuevo_cliente = {
            'ID': nuevo_id_cliente,
            'Nombre Comercial': nombre_lead,
            'CIF': lead_data.get('CIF', ''),
            'Razón Social': nombre_lead,  # Usar nombre comercial por defecto
            'Tipo Local': lead_data.get('Tipo Local', ''),
            'Dirección': '',
            'Ciudad': lead_data.get('Ciudad', ''),
            'CP': lead_data.get('CP', ''),
            'Teléfono': lead_data.get('Teléfono', ''),
            'Email': lead_data.get('Email', ''),
            'Nombre Contacto': lead_data.get('Nombre Contacto', ''),
            'Servicio Contratado': 'Por definir',
            'Precio Mensual': 0,
            'Fecha Inicio': datetime.now().date(),
            'Fecha Fin': None,
            'Estado': 'Activo',
            'MRR': 0,
            'Último Servicio': None,
            'Satisfacción (1-5)': 5,
            'Notas': f"Convertido automáticamente desde Lead #{id_lead} el {datetime.now().strftime('%d/%m/%Y')}"
        }
        
        # Debug: mostrar qué vamos a guardar
        st.write("🔍 **Debug - Datos a guardar:**")
        st.json({
            'ID': nuevo_id_cliente,
            'Nombre': nombre_lead,
            'Ciudad': lead_data.get('Ciudad', ''),
            'Teléfono': lead_data.get('Teléfono', '')
        })
        
        # Agregar a CLIENTES_ACTIVOS
        resultado = utils.agregar_fila(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS", nuevo_cliente)
        
        if resultado:
            return True, f"✅ '{nombre_lead}' convertido exitosamente a Cliente #{nuevo_id_cliente}"
        else:
            return False, "Error al guardar en Excel"
        
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        st.error(f"❌ Error detallado:\n```\n{error_detallado}\n```")
        return False, f"Error: {str(e)}"

def mostrar_leads():
    """Gestión de leads"""
    st.subheader("📋 Gestión de Leads")
    
    # Cargar datos
    df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    
    # Botón para agregar nuevo lead
    if st.button("➕ Agregar Nuevo Lead", type="primary"):
        st.session_state.agregar_lead = True
    
    # Formulario de nuevo lead
    if st.session_state.get('agregar_lead', False):
        with st.form("form_nuevo_lead"):
            st.write("**Nuevo Lead**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre Comercial*")
                tipo_local = st.selectbox("Tipo de Local", config.TIPOS_LOCAL)
                ciudad = st.text_input("Ciudad")
                telefono = st.text_input("Teléfono")
                contacto = st.text_input("Nombre Contacto")
            
            with col2:
                email = st.text_input("Email")
                cp = st.text_input("Código Postal")
                fuente = st.selectbox("Fuente de Captación", config.FUENTES_CAPTACION)
                estado = st.selectbox("Estado", config.ESTADOS_LEAD)
                prioridad = st.selectbox("Prioridad", config.PRIORIDADES)
            
            notas = st.text_area("Notas")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Lead", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not nombre:
                    st.error("El nombre comercial es obligatorio")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_CRM, "LEADS")
                    
                    print(f"[DEBUG] === CREANDO NUEVO LEAD ===")
                    print(f"[DEBUG] Nombre: {nombre}")
                    print(f"[DEBUG] Estado seleccionado: '{estado}'")
                    
                    nuevo_lead = {
                        'ID': nuevo_id,
                        'Nombre Comercial': nombre,
                        'Tipo Local': tipo_local,
                        'Ciudad': ciudad,
                        'CP': cp,
                        'Teléfono': telefono,
                        'Email': email,
                        'Nombre Contacto': contacto,
                        'Estado Lead': estado,
                        'Fuente Captación': fuente,
                        'Fecha Contacto': datetime.now().date(),
                        'Prioridad': prioridad,
                        'Próxima Acción': '',
                        'Fecha Próxima Acción': None,
                        'Comercial Asignado': '',
                        'Facturación Estimada': 0,
                        'Nº Empleados': 0,
                        'URL Google Maps': '',
                        'Rating Google': 0,
                        'Nº Reseñas': 0,
                        'Notas': notas
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_CRM, "LEADS", nuevo_lead):
                        st.success(f"✅ Lead #{nuevo_id} creado correctamente")
                        
                        # Verificar si debe convertirse
                        print(f"[DEBUG] ¿Convertir a cliente? Estado == 'Cliente': {estado == 'Cliente'}")
                        
                        # Si el estado es "Cliente", convertir automáticamente
                        if estado == "Cliente":
                            print(f"[DEBUG] 🎯 INICIANDO CONVERSIÓN A CLIENTE...")
                            
                            # Pequeña pausa para asegurar que OneDrive sincroniza
                            time.sleep(0.5)
                            
                            # Recargar leads después de guardar
                            df_leads_temp = pd.read_excel(config.ARCHIVO_CRM, sheet_name="LEADS")
                            print(f"[DEBUG] Leads recargados: {len(df_leads_temp)} filas")
                            
                            exito, mensaje = convertir_lead_a_cliente(nuevo_id, df_leads_temp)
                            print(f"[DEBUG] Resultado conversión: éxito={exito}, mensaje={mensaje}")
                            
                            if exito:
                                st.success(f"🎉 {mensaje}")
                                
                                # Verificación adicional - leer directamente para confirmar
                                time.sleep(0.5)
                                df_verif = pd.read_excel(config.ARCHIVO_CRM, sheet_name="CLIENTES_ACTIVOS")
                                if not df_verif.empty:
                                    ultimo_cliente = df_verif.iloc[-1]
                                    st.info(f"✅ Verificado: Cliente #{ultimo_cliente['ID']} - {ultimo_cliente['Nombre Comercial']} guardado en Excel")
                                    st.info("📋 Ve a la pestaña 'Clientes Activos' y presiona el botón 🔄 Refrescar si no lo ves")
                            else:
                                st.error(f"⚠️ {mensaje}")
                        else:
                            print(f"[DEBUG] ℹ️  No se convierte porque estado es '{estado}', no 'Cliente'")
                        
                        st.session_state.agregar_lead = False
                        time.sleep(1)
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_lead = False
                st.rerun()
    
    # Mostrar tabla de leads
    st.markdown("---")
    
    if not df_leads.empty:
        # Sección de cambio rápido de estado
        with st.expander("⚡ Cambio Rápido de Estado (Conversión Automática a Cliente)"):
            st.write("**Cambia el estado de un lead. Si seleccionas 'Cliente', se convertirá automáticamente.**")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Crear lista de leads
                opciones_leads = [f"{row['ID']} - {row['Nombre Comercial']}" for _, row in df_leads.iterrows()]
                lead_seleccionado = st.selectbox("Seleccionar Lead", opciones_leads, key="cambiar_estado_lead")
            
            with col2:
                nuevo_estado = st.selectbox("Nuevo Estado", config.ESTADOS_LEAD, key="nuevo_estado_lead")
            
            with col3:
                st.write("")
                st.write("")
                if st.button("🔄 Cambiar Estado", use_container_width=True):
                    id_lead = int(lead_seleccionado.split(" - ")[0])
                    
                    # Actualizar estado en el DataFrame
                    df_leads_actualizado = df_leads.copy()
                    df_leads_actualizado.loc[df_leads_actualizado['ID'] == id_lead, 'Estado Lead'] = nuevo_estado
                    
                    if utils.escribir_excel(config.ARCHIVO_CRM, "LEADS", df_leads_actualizado):
                        st.success(f"✅ Estado actualizado a '{nuevo_estado}'")
                        
                        # Si el nuevo estado es "Cliente", convertir automáticamente
                        if nuevo_estado == "Cliente":
                            exito, mensaje = convertir_lead_a_cliente(id_lead, df_leads_actualizado)
                            
                            if exito:
                                st.success(f"🎉 {mensaje}")
                                st.balloons()
                                st.info("📋 Ve a la pestaña 'Clientes Activos' para verlo")
                            else:
                                st.error(f"⚠️ {mensaje}")
                        
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
        
        st.markdown("---")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_estado = st.multiselect("Filtrar por Estado", 
                                          df_leads['Estado Lead'].unique() if 'Estado Lead' in df_leads.columns else [])
        with col2:
            filtro_prioridad = st.multiselect("Filtrar por Prioridad", 
                                             df_leads['Prioridad'].unique() if 'Prioridad' in df_leads.columns else [])
        with col3:
            buscar = st.text_input("🔍 Buscar por nombre", key="buscar_leads")
        
        # Aplicar filtros
        df_filtrado = df_leads.copy()
        
        if filtro_estado:
            df_filtrado = df_filtrado[df_filtrado['Estado Lead'].isin(filtro_estado)]
        
        if filtro_prioridad:
            df_filtrado = df_filtrado[df_filtrado['Prioridad'].isin(filtro_prioridad)]
        
        if buscar:
            df_filtrado = df_filtrado[df_filtrado['Nombre Comercial'].str.contains(buscar, case=False, na=False)]
        
        # Mostrar tabla
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_leads)} leads")
    else:
        st.info("No hay leads registrados. ¡Agrega el primero!")

def mostrar_clientes_activos():
    """Gestión de clientes activos con edición"""
    st.subheader("✅ Clientes Activos")
    
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    if df_clientes.empty:
        st.info("No hay clientes activos todavía. Los leads se convierten automáticamente cuando cambias su estado a 'Cliente'.")
        return
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clientes", len(df_clientes))
    
    with col2:
        if 'MRR' in df_clientes.columns:
            mrr = df_clientes['MRR'].sum()
            st.metric("MRR Total", f"{mrr:.0f}€")
    
    with col3:
        if 'Satisfacción (1-5)' in df_clientes.columns:
            satisfaccion = df_clientes['Satisfacción (1-5)'].mean()
            color = "normal" if satisfaccion >= 4 else "inverse"
            st.metric("Satisfacción Media", f"{satisfaccion:.1f}/5", delta_color=color)
    
    with col4:
        activos = len(df_clientes[df_clientes['Estado'] == 'Activo']) if 'Estado' in df_clientes.columns else 0
        st.metric("Activos", activos)
    
    st.markdown("---")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Estado' in df_clientes.columns:
            estados_disponibles = df_clientes['Estado'].unique().tolist()
            # Solo poner "Activo" como default si existe
            default_estados = ["Activo"] if "Activo" in estados_disponibles else []
            filtro_estado = st.multiselect("Filtrar por Estado", estados_disponibles, default=default_estados)
        else:
            filtro_estado = []
    
    with col2:
        if 'Tipo Local' in df_clientes.columns:
            tipos = df_clientes['Tipo Local'].unique().tolist()
            filtro_tipo = st.multiselect("Filtrar por Tipo", tipos)
        else:
            filtro_tipo = []
    
    with col3:
        buscar = st.text_input("🔍 Buscar cliente", key="buscar_clientes_activos")
    
    # Aplicar filtros
    df_filtrado = df_clientes.copy()
    
    if filtro_estado:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(filtro_estado)]
    
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado['Tipo Local'].isin(filtro_tipo)]
    
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado['Nombre Comercial'].str.contains(buscar, case=False, na=False) |
            df_filtrado['Ciudad'].str.contains(buscar, case=False, na=False) if 'Ciudad' in df_filtrado.columns else False
        ]
    
    st.markdown("---")
    
    # Mostrar tabla con botón de editar por fila
    if not df_filtrado.empty:
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_clientes)} clientes")
        
        for idx, row in df_filtrado.iterrows():
            with st.container():
                # Crear tarjeta por cliente
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['Nombre Comercial']}**")
                    if 'Ciudad' in row:
                        st.caption(f"📍 {row.get('Ciudad', 'N/A')} | {row.get('Tipo Local', 'N/A')}")
                
                with col2:
                    if 'Servicio Contratado' in row:
                        st.write(f"📋 {row.get('Servicio Contratado', 'N/A')}")
                
                with col3:
                    if 'MRR' in row:
                        mrr_valor = row.get('MRR', 0)
                        st.write(f"💰 {mrr_valor:.0f}€/mes")
                
                with col4:
                    if 'Satisfacción (1-5)' in row:
                        satisf = row.get('Satisfacción (1-5)', 0)
                        estrellas = "⭐" * int(satisf) if satisf > 0 else "☆☆☆☆☆"
                        st.write(f"{estrellas} ({satisf:.1f})")
                
                with col5:
                    if st.button("✏️", key=f"edit_{row['ID']}", use_container_width=True, help="Editar cliente"):
                        st.session_state.editando_cliente = row['ID']
                        st.rerun()
                
                st.markdown("---")
    else:
        st.warning("No hay clientes que coincidan con los filtros")
    
    # Modal de edición
    if st.session_state.get('editando_cliente'):
        id_cliente = st.session_state.editando_cliente
        cliente = df_clientes[df_clientes['ID'] == id_cliente].iloc[0]
        
        st.markdown("---")
        st.subheader(f"✏️ Editando: {cliente['Nombre Comercial']}")
        
        with st.form("form_editar_cliente"):
            st.write(f"**Cliente ID: {id_cliente}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_comercial = st.text_input("Nombre Comercial*", value=cliente.get('Nombre Comercial', ''), key="edit_nombre")
                
                cif = st.text_input("CIF", value=cliente.get('CIF', ''), key="edit_cif")
                
                razon_social = st.text_input("Razón Social", value=cliente.get('Razón Social', ''), key="edit_razon")
                
                tipo_local = st.selectbox("Tipo de Local", 
                    ["Bar", "Restaurante", "Cafetería", "Hotel", "Catering", "Otro"],
                    index=["Bar", "Restaurante", "Cafetería", "Hotel", "Catering", "Otro"].index(cliente.get('Tipo Local', 'Bar')) if cliente.get('Tipo Local') in ["Bar", "Restaurante", "Cafetería", "Hotel", "Catering", "Otro"] else 0,
                    key="edit_tipo")
                
                direccion = st.text_input("Dirección", value=cliente.get('Dirección', ''), key="edit_direccion")
                
                col_ciudad, col_cp = st.columns(2)
                with col_ciudad:
                    ciudad = st.text_input("Ciudad", value=cliente.get('Ciudad', ''), key="edit_ciudad")
                with col_cp:
                    cp = st.text_input("CP", value=cliente.get('CP', ''), key="edit_cp")
            
            with col2:
                telefono = st.text_input("Teléfono", value=cliente.get('Teléfono', ''), key="edit_telefono")
                
                email = st.text_input("Email", value=cliente.get('Email', ''), key="edit_email")
                
                nombre_contacto = st.text_input("Nombre Contacto", value=cliente.get('Nombre Contacto', ''), key="edit_contacto")
                
                servicio = st.selectbox("Servicio Contratado*",
                    ["Por definir", "Básico", "Premium", "Cuota Mensual", "Proyecto Puntual"],
                    index=["Por definir", "Básico", "Premium", "Cuota Mensual", "Proyecto Puntual"].index(cliente.get('Servicio Contratado', 'Por definir')) if cliente.get('Servicio Contratado') in ["Por definir", "Básico", "Premium", "Cuota Mensual", "Proyecto Puntual"] else 0,
                    key="edit_servicio")
                
                precio_mensual = st.number_input("Precio Mensual (€)", 
                    min_value=0.0, value=float(cliente.get('Precio Mensual', 0)), step=50.0, format="%.2f", key="edit_precio")
                
                estado = st.selectbox("Estado*",
                    ["Activo", "Pausado", "Baja"],
                    index=["Activo", "Pausado", "Baja"].index(cliente.get('Estado', 'Activo')) if cliente.get('Estado') in ["Activo", "Pausado", "Baja"] else 0,
                    key="edit_estado")
                
                satisfaccion = st.slider("Satisfacción (1-5)", 
                    min_value=1, max_value=5, value=int(cliente.get('Satisfacción (1-5)', 5)), key="edit_satisfaccion")
            
            notas = st.text_area("Notas", value=cliente.get('Notas', ''), height=100, key="edit_notas")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True, type="primary")
            
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not nombre_comercial:
                    st.error("El nombre comercial es obligatorio")
                else:
                    # Actualizar datos
                    df_actualizado = df_clientes.copy()
                    
                    # Calcular MRR
                    mrr = precio_mensual if estado == "Activo" else 0
                    
                    # Actualizar la fila
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Nombre Comercial'] = nombre_comercial
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'CIF'] = cif
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Razón Social'] = razon_social
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Tipo Local'] = tipo_local
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Dirección'] = direccion
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Ciudad'] = ciudad
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'CP'] = cp
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Teléfono'] = telefono
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Email'] = email
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Nombre Contacto'] = nombre_contacto
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Servicio Contratado'] = servicio
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Precio Mensual'] = precio_mensual
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Estado'] = estado
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'MRR'] = mrr
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Satisfacción (1-5)'] = satisfaccion
                    df_actualizado.loc[df_actualizado['ID'] == id_cliente, 'Notas'] = notas
                    
                    if utils.escribir_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS", df_actualizado):
                        st.success(f"✅ Cliente '{nombre_comercial}' actualizado correctamente")
                        
                        # Si cambió el estado a Baja o Pausado, mostrar alerta
                        if estado != "Activo" and cliente.get('Estado') == "Activo":
                            st.warning(f"⚠️ Cliente marcado como '{estado}'. MRR actualizado a 0€.")
                        
                        # Si cambió de Baja/Pausado a Activo
                        if estado == "Activo" and cliente.get('Estado') != "Activo":
                            st.success(f"🎉 Cliente reactivado. MRR: {precio_mensual}€/mes")
                        
                        del st.session_state.editando_cliente
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error al guardar los cambios")
            
            if cancelar:
                del st.session_state.editando_cliente
                st.rerun()

def mostrar_interacciones():
    """Historial de interacciones"""
    st.subheader("📞 Historial de Interacciones")
    
    # Cargar datos
    df_inter = utils.leer_excel(config.ARCHIVO_CRM, "INTERACCIONES")
    df_leads = utils.leer_excel(config.ARCHIVO_CRM, "LEADS")
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    # Crear lista de clientes disponibles
    clientes_disponibles = []
    if not df_leads.empty and 'ID' in df_leads.columns and 'Nombre Comercial' in df_leads.columns:
        for _, row in df_leads.iterrows():
            clientes_disponibles.append(f"{row['ID']} - {row['Nombre Comercial']}")
    if not df_clientes.empty and 'ID' in df_clientes.columns and 'Nombre Comercial' in df_clientes.columns:
        for _, row in df_clientes.iterrows():
            clientes_disponibles.append(f"{row['ID']} - {row['Nombre Comercial']}")
    
    # Botón para agregar nueva interacción
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nueva Interacción", type="primary", use_container_width=True):
            st.session_state.agregar_interaccion = True
    
    # Formulario de nueva interacción
    if st.session_state.get('agregar_interaccion', False):
        with st.form("form_nueva_interaccion"):
            st.write("**📞 Registrar Nueva Interacción**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if clientes_disponibles:
                    cliente_sel = st.selectbox("Cliente/Lead*", clientes_disponibles)
                    id_cliente = int(cliente_sel.split(" - ")[0])
                    nombre_cliente = cliente_sel.split(" - ")[1]
                else:
                    st.error("No hay clientes ni leads registrados. Agrega uno primero.")
                    id_cliente = 0
                    nombre_cliente = ""
                
                tipo_interaccion = st.selectbox("Tipo de Interacción*", 
                    ["Visita", "Llamada", "Email", "WhatsApp", "Reunión", "Videollamada"])
                
                resultado = st.selectbox("Resultado*", 
                    ["Positivo", "Negativo", "Neutro", "Seguimiento Necesario"])
            
            with col2:
                fecha_interaccion = st.date_input("Fecha*", value=datetime.now().date())
                hora_interaccion = st.time_input("Hora*", value=datetime.now().time())
                
                responsable = st.text_input("Usuario Responsable*", 
                    value=st.session_state.get('usuario_actual', 'Usuario'))
            
            descripcion = st.text_area("Descripción de la Interacción*", 
                placeholder="Ej: Reunión para presentar servicio de escandallo. Cliente mostró interés en optimizar costes...")
            
            proxima_accion = st.text_input("Próxima Acción",
                placeholder="Ej: Enviar propuesta económica")
            
            fecha_proxima = st.date_input("Fecha Próxima Acción", value=None)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Interacción", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not clientes_disponibles:
                    st.error("No puedes crear interacciones sin clientes o leads")
                elif not descripcion:
                    st.error("La descripción es obligatoria")
                else:
                    # Combinar fecha y hora
                    fecha_hora = datetime.combine(fecha_interaccion, hora_interaccion)
                    
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_CRM, "INTERACCIONES")
                    
                    nueva_interaccion = {
                        'ID Interacción': nuevo_id,
                        'ID Cliente': id_cliente,
                        'Nombre Cliente': nombre_cliente,
                        'Fecha': fecha_hora,
                        'Tipo': tipo_interaccion,
                        'Resultado': resultado,
                        'Descripción': descripcion,
                        'Próxima Acción': proxima_accion,
                        'Fecha Próxima Acción': fecha_proxima,
                        'Responsable': responsable
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_CRM, "INTERACCIONES", nueva_interaccion):
                        st.success(f"✅ Interacción #{nuevo_id} registrada correctamente")
                        st.session_state.agregar_interaccion = False
                        st.cache_data.clear()
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_interaccion = False
                st.rerun()
    
    # Mostrar tabla de interacciones
    st.markdown("---")
    
    if not df_inter.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Tipo' in df_inter.columns:
                filtro_tipo = st.multiselect("Filtrar por Tipo", 
                    df_inter['Tipo'].unique())
        
        with col2:
            if 'Resultado' in df_inter.columns:
                filtro_resultado = st.multiselect("Filtrar por Resultado", 
                    df_inter['Resultado'].unique())
        
        with col3:
            if 'Nombre Cliente' in df_inter.columns:
                buscar_cliente = st.text_input("🔍 Buscar cliente", key="buscar_interacciones")
        
        # Aplicar filtros
        df_filtrado = df_inter.copy()
        
        if 'filtro_tipo' in locals() and filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(filtro_tipo)]
        
        if 'filtro_resultado' in locals() and filtro_resultado:
            df_filtrado = df_filtrado[df_filtrado['Resultado'].isin(filtro_resultado)]
        
        if 'buscar_cliente' in locals() and buscar_cliente:
            df_filtrado = df_filtrado[df_filtrado['Nombre Cliente'].str.contains(buscar_cliente, case=False, na=False)]
        
        # Ordenar por fecha descendente
        if 'Fecha' in df_filtrado.columns:
            df_filtrado = df_filtrado.sort_values('Fecha', ascending=False)
        
        # Mostrar métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Interacciones", len(df_filtrado))
        with col2:
            if 'Tipo' in df_filtrado.columns:
                mas_comun = df_filtrado['Tipo'].mode()[0] if not df_filtrado['Tipo'].mode().empty else "N/A"
                st.metric("Tipo más común", mas_comun)
        with col3:
            if 'Resultado' in df_filtrado.columns:
                positivas = len(df_filtrado[df_filtrado['Resultado'] == 'Positivo'])
                st.metric("Interacciones Positivas", positivas)
        with col4:
            if 'Fecha Próxima Acción' in df_filtrado.columns:
                pendientes = df_filtrado['Fecha Próxima Acción'].notna().sum()
                st.metric("Acciones Pendientes", pendientes)
        
        st.markdown("---")
        
        # Mostrar tabla
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_inter)} interacciones")
    else:
        st.info("📞 No hay interacciones registradas. ¡Registra la primera!")

def mostrar_servicios():
    """Historial de servicios"""
    st.subheader("💼 Servicios Prestados")
    
    df_serv = utils.leer_excel(config.ARCHIVO_CRM, "SERVICIOS")
    
    if not df_serv.empty:
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_facturado = df_serv['Precio'].sum() if 'Precio' in df_serv.columns else 0
            st.metric("Total Facturado", utils.formatear_moneda(total_facturado))
        
        with col2:
            total_ahorro = df_serv['Ahorro Generado'].sum() if 'Ahorro Generado' in df_serv.columns else 0
            st.metric("Ahorro Generado", utils.formatear_moneda(total_ahorro))
        
        with col3:
            if total_facturado > 0:
                roi = (total_ahorro / total_facturado)
                st.metric("ROI Medio", f"{roi:.2f}x")
        
        st.markdown("---")
        
        st.dataframe(
            df_serv,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay servicios registrados")

# ============================================================================
# MÓDULO: ESCANDALLOS
# ============================================================================

def modulo_escandallos():
    """Módulo de gestión de escandallos y carta - Por Cliente"""
    st.markdown('<h1 class="main-header">🍽️ Gestión de Escandallos</h1>', unsafe_allow_html=True)
    
    # Cargar clientes activos
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    if df_clientes.empty or len(df_clientes) == 0:
        st.warning("⚠️ No hay clientes activos.")
        st.info("💡 **Cómo empezar:**")
        st.write("1. Ve a **CRM → Leads**")
        st.write("2. Agrega un Lead o cambia el estado de uno existente a **'Cliente'**")
        st.write("3. El sistema lo convertirá automáticamente a Cliente Activo")
        st.write("4. Vuelve aquí para gestionar sus escandallos")
        return
    
    # ========== SELECTOR DE CLIENTE ==========
    st.markdown("### 👤 Selecciona el Cliente")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        opciones_clientes = [f"{row['ID']} - {row['Nombre Comercial']}" 
                            for _, row in df_clientes.iterrows()]
        
        # Recordar el cliente seleccionado
        if 'cliente_escandallo_actual' not in st.session_state:
            st.session_state.cliente_escandallo_actual = 0
        
        indice_default = st.session_state.cliente_escandallo_actual
        
        cliente_seleccionado = st.selectbox(
            "Trabajar con:",
            opciones_clientes,
            index=indice_default,
            key="selector_cliente_escandallos",
            help="Selecciona el cliente para gestionar su carta, escandallos y compras"
        )
        
        # Guardar índice seleccionado
        st.session_state.cliente_escandallo_actual = opciones_clientes.index(cliente_seleccionado)
        
        id_cliente = int(cliente_seleccionado.split(" - ")[0])
        nombre_cliente = cliente_seleccionado.split(" - ")[1]
    
    with col2:
        # Info del cliente
        cliente_info = df_clientes[df_clientes['ID'] == id_cliente].iloc[0]
        st.metric("Tipo", cliente_info.get('Tipo Local', 'N/A'))
    
    with col3:
        st.metric("Ciudad", cliente_info.get('Ciudad', 'N/A'))
    
    st.markdown("---")
    
    # ========== TABS DEL CLIENTE ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍴 Carta", 
        "🔍 Escandallos", 
        "📊 Ingredientes", 
        "💰 Compras"
    ])
    
    with tab1:
        mostrar_carta_cliente(id_cliente, nombre_cliente)
    
    with tab2:
        mostrar_escandallos_cliente(id_cliente, nombre_cliente)
    
    with tab3:
        mostrar_ingredientes_cliente(id_cliente, nombre_cliente)
    
    with tab4:
        mostrar_compras_cliente(id_cliente, nombre_cliente)

def mostrar_carta_cliente(id_cliente, nombre_cliente):
    """Carta del cliente seleccionado"""
    st.subheader(f"🍴 Carta de {nombre_cliente}")
    
    # Cargar platos solo de este cliente
    df_carta_completa = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_carta = df_carta_completa[df_carta_completa['ID Cliente'] == id_cliente] if not df_carta_completa.empty else pd.DataFrame()
    
    # Botón agregar
    if st.button("➕ Agregar Plato a la Carta", type="primary", key="btn_agregar_plato"):
        st.session_state.agregar_plato = True
    
    # Formulario nuevo plato
    if st.session_state.get('agregar_plato', False):
        with st.form("form_nuevo_plato"):
            st.write(f"**Nuevo plato para {nombre_cliente}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_plato = st.text_input("Nombre del Plato*", 
                    placeholder="Ej: Cachopo de ternera", key="nombre_plato_form")
                
                categoria = st.selectbox("Categoría*", config.CATEGORIAS_PLATO, key="cat_plato_form")
                
                precio_venta = st.number_input("Precio de Venta (€)*", 
                    min_value=0.0, value=0.0, step=0.5, format="%.2f", key="precio_plato_form")
            
            with col2:
                coste_total = st.number_input("Coste Total (€)", 
                    min_value=0.0, value=0.0, step=0.1, format="%.2f",
                    help="Se calculará automáticamente desde escandallos", key="coste_plato_form")
                
                ventas_mes = st.number_input("Ventas/Mes Estimadas", 
                    min_value=0, value=0, step=5, key="ventas_plato_form")
                
                activo = st.selectbox("Estado", ["Sí", "No"], key="activo_plato_form")
            
            notas = st.text_area("Notas", placeholder="Notas del plato", key="notas_plato_form")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not nombre_plato:
                    st.error("El nombre es obligatorio")
                elif precio_venta <= 0:
                    st.error("El precio debe ser mayor que 0")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                    
                    margen_euros = precio_venta - coste_total
                    margen_pct = (margen_euros / precio_venta * 100) if precio_venta > 0 else 0
                    food_cost = (coste_total / precio_venta * 100) if precio_venta > 0 else 0
                    
                    if margen_pct >= 60 and ventas_mes >= 50:
                        clasificacion = "Estrella"
                    elif margen_pct >= 60 and ventas_mes < 50:
                        clasificacion = "Rompecabezas"
                    elif margen_pct < 60 and ventas_mes >= 50:
                        clasificacion = "Caballo"
                    else:
                        clasificacion = "Perro"
                    
                    nuevo_plato = {
                        'ID Plato': nuevo_id,
                        'ID Cliente': id_cliente,
                        'Nombre Cliente': nombre_cliente,
                        'Nombre Plato': nombre_plato,
                        'Categoría': categoria,
                        'Precio Venta': precio_venta,
                        'Coste Total': coste_total,
                        'Margen €': margen_euros,
                        'Margen %': margen_pct,
                        'Food Cost %': food_cost,
                        'Ventas/Mes': ventas_mes,
                        'Clasificación': clasificacion,
                        'Precio Recomendado': coste_total * 3,
                        'Activo': activo,
                        'Notas': notas
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", nuevo_plato):
                        st.success(f"✅ '{nombre_plato}' agregado")
                        st.session_state.agregar_plato = False
                        time.sleep(0.5)
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_plato = False
                st.rerun()
    
    # Mostrar carta
    st.markdown("---")
    
    if not df_carta.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Platos", len(df_carta))
        with col2:
            margen = df_carta['Margen %'].mean() if 'Margen %' in df_carta.columns else 0
            st.metric("Margen Medio", f"{margen:.1f}%")
        with col3:
            estrellas = len(df_carta[df_carta['Clasificación'] == 'Estrella']) if 'Clasificación' in df_carta.columns else 0
            st.metric("⭐ Estrellas", estrellas)
        with col4:
            activos = len(df_carta[df_carta['Activo'] == 'Sí']) if 'Activo' in df_carta.columns else 0
            st.metric("Activos", activos)
        
        st.markdown("---")
        
        if 'Margen %' in df_carta.columns:
            bajo = df_carta[df_carta['Margen %'] < config.UMBRAL_MARGEN_MINIMO]
            if not bajo.empty:
                st.warning(f"⚠️ {len(bajo)} platos con margen bajo")
        
        st.dataframe(df_carta, use_container_width=True, hide_index=True)
    else:
        st.info(f"🍽️ {nombre_cliente} no tiene platos. ¡Agrega el primero!")

def mostrar_escandallos_cliente(id_cliente, nombre_cliente):
    """Escandallos del cliente seleccionado"""
    st.subheader(f"🔍 Escandallos de {nombre_cliente}")
    
    df_esc_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
    df_platos_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    
    # Filtrar platos de este cliente
    df_platos = df_platos_completo[df_platos_completo['ID Cliente'] == id_cliente] if not df_platos_completo.empty else pd.DataFrame()
    
    if df_platos.empty:
        st.warning(f"⚠️ {nombre_cliente} no tiene platos. Agrega platos en la pestaña 'Carta' primero.")
        return
    
    # Lista de platos del cliente
    platos_cliente = [f"{row['ID Plato']} - {row['Nombre Plato']}" for _, row in df_platos.iterrows()]
    ingredientes_disp = [f"{row['ID Ingrediente']} - {row['Nombre']}" for _, row in df_ing.iterrows()] if not df_ing.empty else []
    
    # Selector de plato + botón
    col1, col2 = st.columns([3, 1])
    
    with col1:
        plato_ver = st.selectbox("Ver escandallo de:", ["📋 Todos"] + platos_cliente, key="ver_escandallo")
    
    with col2:
        if st.button("➕ Agregar Ingrediente", type="primary", key="btn_agregar_ingrediente"):
            st.session_state.agregar_escandallo = True
    
    # Formulario agregar ingrediente
    if st.session_state.get('agregar_escandallo', False):
        with st.form("form_escandallo"):
            st.write("**Agregar ingrediente al escandallo**")
            
            # Cargar precios de este cliente
            df_precios_cliente = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
            df_precios_cliente = df_precios_cliente[df_precios_cliente['ID Cliente'] == id_cliente]
            
            if df_precios_cliente.empty:
                st.error(f"⚠️ {nombre_cliente} no tiene ingredientes asignados.")
                st.info("Ve a la pestaña 'Ingredientes' y asigna ingredientes primero.")
                
                col1, col2 = st.columns(2)
                with col2:
                    cancelar = st.form_submit_button("❌ Cerrar", use_container_width=True)
                if cancelar:
                    st.session_state.agregar_escandallo = False
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    plato_sel = st.selectbox("Plato*", platos_cliente, key="plato_esc_form")
                    id_plato = int(plato_sel.split(" - ")[0])
                    nombre_plato = plato_sel.split(" - ")[1]
                    
                    # Lista de ingredientes del cliente
                    opciones_ing_cliente = [f"{row['ID Ingrediente']} - {row['Nombre Ingrediente']}" 
                                           for _, row in df_precios_cliente.iterrows()]
                    
                    ing_sel = st.selectbox("Ingrediente* (asignados a este cliente)", 
                                          opciones_ing_cliente, key="ing_esc_form")
                    id_ing = int(ing_sel.split(" - ")[0])
                    nombre_ing = ing_sel.split(" - ")[1]
                    
                    # Obtener precio del cliente
                    precio_ing = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing]['Precio Cliente'].values[0]
                    unidad_ing = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing]['Unidad'].values[0]
                    precio_mercado = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing]['Precio Mercado Referencia'].values[0]
                    
                    st.caption(f"Precio de este cliente: {precio_ing:.2f}€/{unidad_ing}")
                    st.caption(f"Precio mercado: {precio_mercado:.2f}€/{unidad_ing}")
                
                with col2:
                    cantidad = st.number_input(f"Cantidad ({unidad_ing})*", 
                        min_value=0.0, value=0.0, step=0.01, format="%.3f", key="cant_esc_form")
                    
                    if cantidad > 0:
                        coste = cantidad * precio_ing
                        st.metric("Coste Total", f"{coste:.2f} €")
                    
                    proveedor = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing]['Proveedor'].values[0]
                    st.text_input("Proveedor", value=proveedor, key="prov_esc_form", disabled=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Guardar", use_container_width=True)
                with col2:
                    cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    if cantidad <= 0:
                        st.error("La cantidad debe ser mayor que 0")
                    else:
                        nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                        coste_total = cantidad * precio_ing
                        
                        nuevo_esc = {
                            'ID Escandallo': nuevo_id,
                            'ID Plato': id_plato,
                            'Nombre Plato': nombre_plato,
                            'ID Ingrediente': id_ing,
                            'Nombre Ingrediente': nombre_ing,
                            'Cantidad': cantidad,
                            'Unidad': unidad_ing,
                            'Coste Unitario': precio_ing,
                            'Coste Total': coste_total,
                            '% del Plato': 0,
                            'Proveedor Actual': proveedor,
                            'Última Actualización': datetime.now().date()
                        }
                        
                        if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", nuevo_esc):
                            st.success(f"✅ Ingrediente agregado (coste: {coste_total:.2f}€)")
                            utils.recalcular_costes_platos(utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS"))
                            st.session_state.agregar_escandallo = False
                            time.sleep(0.5)
                            st.rerun()
                
                if cancelar:
                    st.session_state.agregar_escandallo = False
                    st.rerun()
    
    # Mostrar escandallos
    st.markdown("---")
    
    # Filtrar escandallos por platos del cliente
    ids_platos_cliente = df_platos['ID Plato'].tolist()
    df_esc = df_esc_completo[df_esc_completo['ID Plato'].isin(ids_platos_cliente)] if not df_esc_completo.empty else pd.DataFrame()
    
    if plato_ver != "📋 Todos":
        id_plato_filtro = int(plato_ver.split(" - ")[0])
        df_esc = df_esc[df_esc['ID Plato'] == id_plato_filtro]
        
        # Resumen del plato
        if not df_esc.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ingredientes", len(df_esc))
            with col2:
                coste = df_esc['Coste Total'].sum() if 'Coste Total' in df_esc.columns else 0
                st.metric("Coste Total", f"{coste:.2f} €")
            with col3:
                plato_info = df_platos[df_platos['ID Plato'] == id_plato_filtro].iloc[0]
                precio = plato_info.get('Precio Venta', 0)
                margen = ((precio - coste) / precio * 100) if precio > 0 else 0
                st.metric("Margen", f"{margen:.1f}%")
            st.markdown("---")
    
    if not df_esc.empty:
        st.dataframe(df_esc, use_container_width=True, hide_index=True)
    else:
        st.info("🔍 No hay escandallos. Agrega ingredientes a los platos.")

def mostrar_compras_cliente(id_cliente, nombre_cliente):
    """Compras del cliente seleccionado"""
    st.subheader(f"💰 Compras de {nombre_cliente}")
    
    df_compras_completo = utils.leer_excel(config.ARCHIVO_OPERACIONES, "COMPRAS_CLIENTE")
    df_compras = df_compras_completo[df_compras_completo['ID Cliente'] == id_cliente] if not df_compras_completo.empty else pd.DataFrame()
    
    if not df_compras.empty:
        st.dataframe(df_compras, use_container_width=True, hide_index=True)
    else:
        st.info(f"💰 {nombre_cliente} no tiene compras registradas todavía.")

def mostrar_escandallos():
    """Vista y gestión de escandallos (ingredientes por plato)"""
    st.subheader("🔍 Escandallos - Desglose por Plato")
    
    # Cargar datos
    df_esc = utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
    df_platos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    
    # Crear listas
    platos_disponibles = []
    if not df_platos.empty and 'ID Plato' in df_platos.columns and 'Nombre Plato' in df_platos.columns:
        for _, row in df_platos.iterrows():
            platos_disponibles.append(f"{row['ID Plato']} - {row['Nombre Plato']} ({row['Nombre Cliente']})")
    
    ingredientes_disponibles = []
    if not df_ing.empty and 'ID Ingrediente' in df_ing.columns and 'Nombre' in df_ing.columns:
        for _, row in df_ing.iterrows():
            ingredientes_disponibles.append(f"{row['ID Ingrediente']} - {row['Nombre']}")
    
    # Botón agregar
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Agregar Ingrediente a Plato", type="primary", use_container_width=True):
            st.session_state.agregar_escandallo = True
    
    # Formulario
    if st.session_state.get('agregar_escandallo', False):
        with st.form("form_nuevo_escandallo"):
            st.write("**🔍 Agregar Ingrediente al Escandallo**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if platos_disponibles:
                    plato_sel = st.selectbox("Plato*", platos_disponibles)
                    id_plato = int(plato_sel.split(" - ")[0])
                    nombre_plato = plato_sel.split(" - ")[1].split(" (")[0]
                else:
                    st.error("No hay platos. Agrega uno primero en 'Carta de Clientes'")
                    id_plato = 0
                    nombre_plato = ""
                
                if ingredientes_disponibles:
                    ing_sel = st.selectbox("Ingrediente*", ingredientes_disponibles)
                    id_ing = int(ing_sel.split(" - ")[0])
                    nombre_ing = ing_sel.split(" - ")[1]
                    
                    # Obtener precio actual del ingrediente
                    precio_ing = df_ing[df_ing['ID Ingrediente'] == id_ing]['Precio Mercado Medio'].values[0]
                    unidad_ing = df_ing[df_ing['ID Ingrediente'] == id_ing]['Unidad Compra'].values[0]
                else:
                    st.error("No hay ingredientes. Agrega uno primero en 'Ingredientes Maestro'")
                    id_ing = 0
                    nombre_ing = ""
                    precio_ing = 0
                    unidad_ing = "KG"
            
            with col2:
                cantidad = st.number_input("Cantidad*", 
                    min_value=0.0, value=0.0, step=0.01, format="%.3f",
                    help=f"Cantidad en {unidad_ing}")
                
                st.metric("Coste Unitario Actual", f"{precio_ing:.4f} €/{unidad_ing}")
                
                if cantidad > 0:
                    coste_calculado = cantidad * precio_ing
                    st.metric("Coste Total Calculado", f"{coste_calculado:.2f} €")
            
            proveedor = st.text_input("Proveedor Actual", 
                placeholder="Opcional: nombre del proveedor habitual")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Agregar al Escandallo", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not platos_disponibles or not ingredientes_disponibles:
                    st.error("Necesitas tener al menos un plato y un ingrediente")
                elif cantidad <= 0:
                    st.error("La cantidad debe ser mayor que 0")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "ESCANDALLOS")
                    
                    coste_total = cantidad * precio_ing
                    
                    nuevo_escandallo = {
                        'ID Escandallo': nuevo_id,
                        'ID Plato': id_plato,
                        'Nombre Plato': nombre_plato,
                        'ID Ingrediente': id_ing,
                        'Nombre Ingrediente': nombre_ing,
                        'Cantidad': cantidad,
                        'Unidad': unidad_ing,
                        'Coste Unitario': precio_ing,
                        'Coste Total': coste_total,
                        '% del Plato': 0,  # Se calculará después
                        'Proveedor Actual': proveedor,
                        'Última Actualización': datetime.now().date()
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "ESCANDALLOS", nuevo_escandallo):
                        st.success(f"✅ Ingrediente agregado al escandallo")
                        st.info(f"💰 Coste: {coste_total:.2f} €")
                        
                        # Recalcular coste total del plato
                        utils.recalcular_costes_platos(utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS"))
                        
                        st.session_state.agregar_escandallo = False
                        st.cache_data.clear()
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_escandallo = False
                st.rerun()
    
    # Mostrar escandallos
    st.markdown("---")
    
    if not df_esc.empty:
        # Filtro por plato
        if 'Nombre Plato' in df_esc.columns:
            platos_unicos = df_esc['Nombre Plato'].unique()
            plato_filtro = st.selectbox("Filtrar por Plato", ["Todos"] + list(platos_unicos))
            
            if plato_filtro != "Todos":
                df_filtrado = df_esc[df_esc['Nombre Plato'] == plato_filtro]
                
                # Mostrar resumen del plato
                if not df_filtrado.empty:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_ingredientes = len(df_filtrado)
                        st.metric("Ingredientes", total_ingredientes)
                    
                    with col2:
                        if 'Coste Total' in df_filtrado.columns:
                            coste_plato = df_filtrado['Coste Total'].sum()
                            st.metric("Coste Total Plato", f"{coste_plato:.2f} €")
                    
                    with col3:
                        # Buscar precio de venta del plato
                        if not df_platos.empty:
                            plato_info = df_platos[df_platos['Nombre Plato'] == plato_filtro]
                            if not plato_info.empty and 'Precio Venta' in plato_info.columns:
                                precio_venta = plato_info['Precio Venta'].values[0]
                                st.metric("Precio Venta", f"{precio_venta:.2f} €")
                    
                    with col4:
                        if 'coste_plato' in locals() and 'precio_venta' in locals() and precio_venta > 0:
                            margen = ((precio_venta - coste_plato) / precio_venta) * 100
                            st.metric("Margen", f"{margen:.1f}%")
                    
                    st.markdown("---")
            else:
                df_filtrado = df_esc
        else:
            df_filtrado = df_esc
        
        # Mostrar tabla
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Coste Unitario": st.column_config.NumberColumn(
                    "Coste Unitario",
                    format="%.4f €"
                ),
                "Coste Total": st.column_config.NumberColumn(
                    "Coste Total",
                    format="%.2f €"
                ),
                "Cantidad": st.column_config.NumberColumn(
                    "Cantidad",
                    format="%.3f"
                ),
                "% del Plato": st.column_config.NumberColumn(
                    "% del Plato",
                    format="%.1f%%"
                )
            }
        )
        
        st.caption(f"Mostrando {len(df_filtrado)} ingredientes")
    else:
        st.info("🔍 No hay escandallos registrados. ¡Agrega ingredientes a tus platos!")

def mostrar_carta():
    """Vista de carta de clientes"""
    st.subheader("🍴 Carta de Clientes")
    
    # Cargar datos
    df_carta = utils.leer_excel(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
    df_clientes = utils.leer_excel(config.ARCHIVO_CRM, "CLIENTES_ACTIVOS")
    
    # Crear lista de clientes
    clientes_disponibles = []
    if not df_clientes.empty and 'ID' in df_clientes.columns and 'Nombre Comercial' in df_clientes.columns:
        for _, row in df_clientes.iterrows():
            clientes_disponibles.append(f"{row['ID']} - {row['Nombre Comercial']}")
    
    # Selector de cliente para filtrar
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not df_carta.empty and 'Nombre Cliente' in df_carta.columns:
            clientes_unicos = df_carta['Nombre Cliente'].unique()
            cliente_filtro = st.selectbox("Filtrar por Cliente", ["Todos"] + list(clientes_unicos))
        else:
            cliente_filtro = "Todos"
    
    with col2:
        if st.button("➕ Agregar Plato", type="primary", use_container_width=True):
            st.session_state.agregar_plato = True
    
    # Formulario de nuevo plato
    if st.session_state.get('agregar_plato', False):
        with st.form("form_nuevo_plato"):
            st.write("**🍽️ Agregar Nuevo Plato a la Carta**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if clientes_disponibles:
                    cliente_sel = st.selectbox("Cliente*", clientes_disponibles)
                    id_cliente = int(cliente_sel.split(" - ")[0])
                    nombre_cliente = cliente_sel.split(" - ")[1]
                else:
                    st.error("No hay clientes activos. Agrega uno primero.")
                    id_cliente = 0
                    nombre_cliente = ""
                
                nombre_plato = st.text_input("Nombre del Plato*", 
                    placeholder="Ej: Cachopo de ternera")
                
                categoria = st.selectbox("Categoría*", config.CATEGORIAS_PLATO)
                
                precio_venta = st.number_input("Precio de Venta (€)*", 
                    min_value=0.0, value=0.0, step=0.5, format="%.2f")
            
            with col2:
                coste_total = st.number_input("Coste Total (€)*", 
                    min_value=0.0, value=0.0, step=0.1, format="%.2f",
                    help="Suma de todos los ingredientes. Se puede calcular automáticamente desde Escandallos")
                
                ventas_mes = st.number_input("Ventas/Mes Estimadas", 
                    min_value=0, value=0, step=5)
                
                activo = st.selectbox("¿Activo en carta?", ["Sí", "No"])
            
            descripcion = st.text_area("Descripción del Plato", 
                placeholder="Opcional: descripción del plato para la carta")
            
            notas = st.text_area("Notas Internas", 
                placeholder="Notas sobre el plato, ingredientes especiales, etc.")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Plato", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not clientes_disponibles:
                    st.error("No puedes agregar platos sin clientes activos")
                elif not nombre_plato:
                    st.error("El nombre del plato es obligatorio")
                elif precio_venta <= 0:
                    st.error("El precio de venta debe ser mayor que 0")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES")
                    
                    # Calcular márgenes
                    margen_euros = precio_venta - coste_total
                    margen_pct = (margen_euros / precio_venta * 100) if precio_venta > 0 else 0
                    food_cost = (coste_total / precio_venta * 100) if precio_venta > 0 else 0
                    
                    # Clasificar según ingeniería de menú
                    if margen_pct >= 60 and ventas_mes >= 50:
                        clasificacion = "Estrella"
                    elif margen_pct >= 60 and ventas_mes < 50:
                        clasificacion = "Rompecabezas"
                    elif margen_pct < 60 and ventas_mes >= 50:
                        clasificacion = "Caballo"
                    else:
                        clasificacion = "Perro"
                    
                    precio_recomendado = coste_total * 3  # Multiplicador estándar
                    
                    nuevo_plato = {
                        'ID Plato': nuevo_id,
                        'ID Cliente': id_cliente,
                        'Nombre Cliente': nombre_cliente,
                        'Nombre Plato': nombre_plato,
                        'Categoría': categoria,
                        'Precio Venta': precio_venta,
                        'Coste Total': coste_total,
                        'Margen €': margen_euros,
                        'Margen %': margen_pct,
                        'Food Cost %': food_cost,
                        'Ventas/Mes': ventas_mes,
                        'Clasificación': clasificacion,
                        'Precio Recomendado': precio_recomendado,
                        'Activo': activo,
                        'Notas': notas
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "CARTA_CLIENTES", nuevo_plato):
                        st.success(f"✅ Plato '{nombre_plato}' agregado correctamente")
                        st.info(f"📊 Margen: {margen_pct:.1f}% | Food Cost: {food_cost:.1f}% | Clasificación: {clasificacion}")
                        st.session_state.agregar_plato = False
                        st.cache_data.clear()
                        st.rerun()
            
            if cancelar:
                st.session_state.agregar_plato = False
                st.rerun()
    
    # Mostrar platos
    st.markdown("---")
    
    if not df_carta.empty:
        # Aplicar filtro de cliente
        df_filtrado = df_carta.copy()
        if cliente_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Nombre Cliente'] == cliente_filtro]
        
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Platos", len(df_filtrado))
        
        with col2:
            if 'Margen %' in df_filtrado.columns:
                margen_medio = df_filtrado['Margen %'].mean()
                st.metric("Margen Medio", f"{margen_medio:.1f}%")
        
        with col3:
            if 'Clasificación' in df_filtrado.columns:
                estrellas = len(df_filtrado[df_filtrado['Clasificación'] == 'Estrella'])
                st.metric("⭐ Estrellas", estrellas)
        
        with col4:
            if 'Activo' in df_filtrado.columns:
                activos = len(df_filtrado[df_filtrado['Activo'] == 'Sí'])
                st.metric("Platos Activos", activos)
        
        st.markdown("---")
        
        # Alertas de márgenes bajos
        if 'Margen %' in df_filtrado.columns:
            platos_bajo_margen = df_filtrado[df_filtrado['Margen %'] < config.UMBRAL_MARGEN_MINIMO]
            if not platos_bajo_margen.empty:
                st.warning(f"⚠️ {len(platos_bajo_margen)} platos con margen bajo (<{config.UMBRAL_MARGEN_MINIMO}%)")
        
        # Mostrar tabla con formato condicional
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Margen %": st.column_config.NumberColumn(
                    "Margen %",
                    format="%.1f%%"
                ),
                "Food Cost %": st.column_config.NumberColumn(
                    "Food Cost %",
                    format="%.1f%%"
                ),
                "Precio Venta": st.column_config.NumberColumn(
                    "Precio Venta",
                    format="%.2f €"
                ),
                "Coste Total": st.column_config.NumberColumn(
                    "Coste Total",
                    format="%.2f €"
                ),
                "Margen €": st.column_config.NumberColumn(
                    "Margen €",
                    format="%.2f €"
                )
            }
        )
        
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_carta)} platos")
    else:
        st.info("🍽️ No hay platos registrados. ¡Agrega el primero!")

def mostrar_ingredientes():
    """Vista de ingredientes maestro (compartido) pero no se usa directamente"""
    st.info("ℹ️ **Nota:** Los ingredientes maestro son solo referencia. Cada cliente tiene sus propios precios.")
    
    if st.button("📊 Ver Base de Ingredientes Maestro", key="ver_ingredientes_maestro"):
        st.session_state.ver_ingredientes_maestro = not st.session_state.get('ver_ingredientes_maestro', False)
    
    if st.session_state.get('ver_ingredientes_maestro', False):
        df_ing = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
        
        if not df_ing.empty:
            st.caption("**Base de datos de referencia** (precio promedio del mercado)")
            st.dataframe(df_ing, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ingredientes en la base maestra")

def mostrar_ingredientes_cliente(id_cliente, nombre_cliente):
    """Ingredientes con precios específicos del cliente seleccionado"""
    st.subheader(f"📊 Ingredientes de {nombre_cliente}")
    
    # Cargar datos
    df_ing_maestro = utils.leer_excel(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
    df_precios_todos = utils.leer_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
    
    # Filtrar precios de este cliente
    df_precios_cliente = df_precios_todos[df_precios_todos['ID Cliente'] == id_cliente] if not df_precios_todos.empty else pd.DataFrame()
    
    st.write("---")
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Asignar Ingrediente a este Cliente", type="primary", key="btn_asignar_ing"):
            st.session_state.asignar_ingrediente_cliente = True
    
    with col2:
        if st.button("🆕 Crear Nuevo Ingrediente en Base", key="btn_nuevo_ing_base"):
            st.session_state.crear_ingrediente_base = True
    
    # Formulario: Asignar ingrediente existente al cliente
    if st.session_state.get('asignar_ingrediente_cliente', False):
        with st.form("form_asignar_ingrediente"):
            st.write(f"**Asignar ingrediente existente a {nombre_cliente}**")
            
            if df_ing_maestro.empty:
                st.error("No hay ingredientes en la base. Crea uno primero.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Lista de ingredientes maestro
                    opciones_ing = [f"{row['ID Ingrediente']} - {row['Nombre']}" 
                                   for _, row in df_ing_maestro.iterrows()]
                    
                    ing_sel = st.selectbox("Ingrediente*", opciones_ing, key="ing_asignar_form")
                    id_ing = int(ing_sel.split(" - ")[0])
                    nombre_ing = ing_sel.split(" - ")[1]
                    
                    # Datos del ingrediente
                    ing_data = df_ing_maestro[df_ing_maestro['ID Ingrediente'] == id_ing].iloc[0]
                    precio_mercado = ing_data['Precio Mercado Medio']
                    unidad = ing_data['Unidad Compra']
                    
                    st.metric("Precio Mercado Medio (Referencia)", f"{precio_mercado:.2f} €/{unidad}")
                
                with col2:
                    precio_cliente = st.number_input(f"Precio para {nombre_cliente} (€/{unidad})*", 
                        min_value=0.0, value=float(precio_mercado), step=0.1, format="%.2f", key="precio_asignar_form")
                    
                    # Calcular desviación
                    if precio_mercado > 0:
                        desviacion = ((precio_cliente - precio_mercado) / precio_mercado) * 100
                        
                        if desviacion > 10:
                            st.error(f"⚠️ +{desviacion:.1f}% MÁS CARO que el mercado")
                        elif desviacion < -10:
                            st.success(f"✅ {abs(desviacion):.1f}% MÁS BARATO que el mercado")
                        else:
                            st.info(f"📊 Desviación: {desviacion:+.1f}%")
                    
                    proveedor = st.text_input("Proveedor", key="prov_asignar_form")
                
                notas = st.text_area("Notas", key="notas_asignar_form")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Asignar a Cliente", use_container_width=True)
                with col2:
                    cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    if precio_cliente <= 0:
                        st.error("El precio debe ser mayor que 0")
                    else:
                        # Verificar si ya existe
                        existe = df_precios_cliente[
                            (df_precios_cliente['ID Cliente'] == id_cliente) & 
                            (df_precios_cliente['ID Ingrediente'] == id_ing)
                        ]
                        
                        if not existe.empty:
                            st.warning(f"⚠️ {nombre_cliente} ya tiene este ingrediente. Usa 'Actualizar Precio' más abajo.")
                        else:
                            nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE")
                            desviacion = ((precio_cliente - precio_mercado) / precio_mercado * 100) if precio_mercado > 0 else 0
                            
                            nuevo_precio = {
                                'ID Precio': nuevo_id,
                                'ID Cliente': id_cliente,
                                'Nombre Cliente': nombre_cliente,
                                'ID Ingrediente': id_ing,
                                'Nombre Ingrediente': nombre_ing,
                                'Precio Cliente': precio_cliente,
                                'Unidad': unidad,
                                'Precio Mercado Referencia': precio_mercado,
                                'Desviación %': desviacion,
                                'Última Actualización': datetime.now().date(),
                                'Proveedor': proveedor,
                                'Notas': notas
                            }
                            
                            if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE", nuevo_precio):
                                st.success(f"✅ {nombre_ing} asignado a {nombre_cliente} a {precio_cliente:.2f}€")
                                st.session_state.asignar_ingrediente_cliente = False
                                time.sleep(0.5)
                                st.rerun()
                
                if cancelar:
                    st.session_state.asignar_ingrediente_cliente = False
                    st.rerun()
    
    # Formulario: Crear nuevo ingrediente en la base
    if st.session_state.get('crear_ingrediente_base', False):
        with st.form("form_nuevo_ingrediente_base"):
            st.write("**Crear nuevo ingrediente en Base Maestro**")
            st.caption("Después podrás asignarlo a clientes con sus precios específicos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_ing = st.text_input("Nombre*", key="nombre_ing_base_form")
                categoria = st.selectbox("Categoría*", config.CATEGORIAS_INGREDIENTE, key="cat_ing_base_form")
                unidad = st.selectbox("Unidad*", ["KG", "Litro", "Unidad", "Docena", "Gramos", "ML"], key="unidad_ing_base_form")
            
            with col2:
                precio_mercado = st.number_input("Precio Mercado Medio (€)*", 
                    min_value=0.0, step=0.1, format="%.2f", key="precio_ing_base_form",
                    help="Precio promedio de referencia")
                estacionalidad = st.text_input("Estacionalidad", key="est_ing_base_form")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Crear en Base", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if not nombre_ing:
                    st.error("El nombre es obligatorio")
                elif precio_mercado <= 0:
                    st.error("El precio debe ser mayor que 0")
                else:
                    nuevo_id = utils.obtener_siguiente_id(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO")
                    
                    nuevo_ing = {
                        'ID Ingrediente': nuevo_id,
                        'Nombre': nombre_ing,
                        'Categoría': categoria,
                        'Unidad Compra': unidad,
                        'Precio Mercado Medio': precio_mercado,
                        'Var % Semana': 0,
                        'Var % Mes': 0,
                        'Última Actualización': datetime.now().date(),
                        'Estacionalidad': estacionalidad,
                        'Notas': ''
                    }
                    
                    if utils.agregar_fila(config.ARCHIVO_OPERACIONES, "INGREDIENTES_MAESTRO", nuevo_ing):
                        st.success(f"✅ '{nombre_ing}' creado en Base Maestro")
                        st.info("Ahora puedes asignarlo a clientes con sus precios específicos")
                        st.session_state.crear_ingrediente_base = False
                        time.sleep(0.5)
                        st.rerun()
            
            if cancelar:
                st.session_state.crear_ingrediente_base = False
                st.rerun()
    
    # Mostrar ingredientes del cliente
    st.markdown("---")
    st.subheader(f"Ingredientes asignados a {nombre_cliente}")
    
    if not df_precios_cliente.empty:
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ingredientes", len(df_precios_cliente))
        
        with col2:
            if 'Precio Cliente' in df_precios_cliente.columns:
                precio_medio = df_precios_cliente['Precio Cliente'].mean()
                st.metric("Precio Medio", f"{precio_medio:.2f} €")
        
        with col3:
            if 'Desviación %' in df_precios_cliente.columns:
                desv_media = df_precios_cliente['Desviación %'].mean()
                color = "normal" if abs(desv_media) < 5 else "inverse"
                st.metric("Desviación Media", f"{desv_media:+.1f}%", delta_color=color)
        
        with col4:
            if 'Desviación %' in df_precios_cliente.columns:
                caros = len(df_precios_cliente[df_precios_cliente['Desviación %'] > 10])
                st.metric("⚠️ Más Caros", caros)
        
        st.markdown("---")
        
        # Actualización rápida de precio
        with st.expander("⚡ Actualización Rápida de Precio"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                opciones_ing_cliente = [f"{row['ID Ingrediente']} - {row['Nombre Ingrediente']}" 
                                       for _, row in df_precios_cliente.iterrows()]
                ing_actualizar = st.selectbox("Ingrediente", opciones_ing_cliente, key="ing_actualizar_select")
                id_ing_act = int(ing_actualizar.split(" - ")[0])
            
            with col2:
                precio_actual = df_precios_cliente[df_precios_cliente['ID Ingrediente'] == id_ing_act]['Precio Cliente'].values[0]
                nuevo_precio = st.number_input("Nuevo Precio (€)", value=float(precio_actual), 
                                              min_value=0.0, step=0.1, format="%.2f", key="nuevo_precio_act")
            
            with col3:
                st.write("")
                st.write("")
                if st.button("🔄 Actualizar", use_container_width=True, key="btn_actualizar_precio"):
                    if nuevo_precio > 0:
                        # Actualizar en PRECIOS_POR_CLIENTE
                        df_precios_actualizado = df_precios_todos.copy()
                        mascara = (df_precios_actualizado['ID Cliente'] == id_cliente) & \
                                 (df_precios_actualizado['ID Ingrediente'] == id_ing_act)
                        
                        precio_mercado_ref = df_precios_actualizado.loc[mascara, 'Precio Mercado Referencia'].values[0]
                        nueva_desv = ((nuevo_precio - precio_mercado_ref) / precio_mercado_ref * 100) if precio_mercado_ref > 0 else 0
                        
                        df_precios_actualizado.loc[mascara, 'Precio Cliente'] = nuevo_precio
                        df_precios_actualizado.loc[mascara, 'Desviación %'] = nueva_desv
                        df_precios_actualizado.loc[mascara, 'Última Actualización'] = datetime.now().date()
                        
                        if utils.escribir_excel(config.ARCHIVO_OPERACIONES, "PRECIOS_POR_CLIENTE", df_precios_actualizado):
                            st.success(f"✅ Precio actualizado a {nuevo_precio:.2f}€")
                            
                            # Recalcular escandallos
                            st.info("♻️ Recalculando escandallos de este cliente...")
                            utils.recalcular_costes_platos(utils.leer_excel(config.ARCHIVO_OPERACIONES, "ESCANDALLOS"))
                            
                            time.sleep(1)
                            st.rerun()
        
        # Tabla de ingredientes
        st.dataframe(
            df_precios_cliente,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Precio Cliente": st.column_config.NumberColumn("Precio Cliente", format="%.2f €"),
                "Precio Mercado Referencia": st.column_config.NumberColumn("Ref. Mercado", format="%.2f €"),
                "Desviación %": st.column_config.NumberColumn("Desviación", format="%+.1f%%")
            }
        )
        
    else:
        st.info(f"📊 {nombre_cliente} no tiene ingredientes asignados. Usa el botón '➕ Asignar Ingrediente' arriba.")
def mostrar_compras():
    """Vista de compras de clientes"""
    st.subheader("💰 Registro de Compras")
    
    df_comp = utils.leer_excel(config.ARCHIVO_OPERACIONES, "COMPRAS_CLIENTE")
    
    if not df_comp.empty:
        st.dataframe(
            df_comp,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay compras registradas")

# ============================================================================
# MÓDULO: PROVEEDORES
# ============================================================================

def modulo_proveedores():
    """Módulo de gestión de proveedores"""
    st.markdown('<h1 class="main-header">🏢 Gestión de Proveedores</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Listado", "📊 Comparativa"])
    
    with tab1:
        df_prov = utils.leer_excel(config.ARCHIVO_PROVEEDORES, "PROVEEDORES")
        
        if not df_prov.empty:
            st.dataframe(df_prov, use_container_width=True, hide_index=True)
        else:
            st.info("No hay proveedores registrados")
    
    with tab2:
        st.subheader("📊 Comparativa de Precios")
        st.info("Funcionalidad en desarrollo")

# ============================================================================
# MÓDULO: EMPRESA
# ============================================================================

def modulo_empresa():
    """Módulo de backoffice y empresa"""
    st.markdown('<h1 class="main-header">💼 Gestión Empresarial</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 KPIs", "💰 Facturación", "📉 Gastos"])
    
    with tab1:
        df_kpis = utils.leer_excel(config.ARCHIVO_EMPRESA, "KPIS_MENSUALES")
        
        if not df_kpis.empty:
            st.dataframe(df_kpis, use_container_width=True, hide_index=True)
        else:
            st.info("No hay KPIs registrados")
    
    with tab2:
        df_fact = utils.leer_excel(config.ARCHIVO_EMPRESA, "FACTURACION")
        
        if not df_fact.empty:
            st.dataframe(df_fact, use_container_width=True, hide_index=True)
        else:
            st.info("No hay facturas registradas")
    
    with tab3:
        df_gastos = utils.leer_excel(config.ARCHIVO_EMPRESA, "GASTOS")
        
        if not df_gastos.empty:
            st.dataframe(df_gastos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay gastos registrados")

# ============================================================================
# MÓDULO: CONFIGURACIÓN
# ============================================================================

def modulo_configuracion():
    """Configuración del sistema"""
    st.markdown('<h1 class="main-header">⚙️ Configuración</h1>', unsafe_allow_html=True)
    
    st.subheader("📁 Rutas del Sistema")
    st.code(f"OneDrive: {config.ONEDRIVE_BASE}")
    st.code(f"Datos: {config.RUTA_DATOS}")
    
    st.markdown("---")
    
    st.subheader("📊 Estado de los Archivos")
    archivos_faltantes = config.verificar_archivos_excel()
    
    if not archivos_faltantes:
        st.success("✅ Todos los archivos Excel están correctamente ubicados")
    else:
        st.error("❌ Archivos faltantes:")
        for archivo in archivos_faltantes:
            st.write(archivo)

# ============================================================================
# MAIN - PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal"""
    
    # Verificar sistema
    verificar_sistema()
    
    # Mostrar sidebar y obtener módulo seleccionado
    modulo = mostrar_sidebar()
    
    # Renderizar módulo seleccionado
    if "Dashboard" in modulo:
        modulo_dashboard()
    elif "CRM" in modulo:
        modulo_crm()
    elif "Escandallos" in modulo:
        modulo_escandallos()
    elif "Proveedores" in modulo:
        modulo_proveedores()
    elif "Empresa" in modulo:
        modulo_empresa()
    elif "Configuración" in modulo:
        modulo_configuracion()

if __name__ == "__main__":
    main()
