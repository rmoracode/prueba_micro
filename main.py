from fastapi import FastAPI, Query
import pandas as pd
from typing import Optional

app = FastAPI()

# Carga y limpieza
df = pd.read_csv('fuente.csv', sep=';')
for col in ['Vol', 'VN']:
    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

# Aseguramos que la columna de Mes/Año sea tratada correctamente para filtrar
# Basado en tu archivo: "abril de 2025" y "abril de 2026"
@app.get("/consultar")
def consultar(
    marca: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    cliente: Optional[str] = Query(None),
    dia: Optional[str] = Query(None)
):
    df_filtrado = df.copy()

    # 1. Aplicación de filtros dinámicos
    dia_final = int(dia) if (dia and dia.strip().isdigit()) else None
    
    filtros = {
        'desc_marca': marca,
        'Region': region,
        'nomb_cliente': cliente,
        'Día de fecha_liquidacion': dia_final
    }

    for columna, valor in filtros.items():
        if valor is not None:
            if isinstance(valor, str):
                df_filtrado = df_filtrado[df_filtrado[columna].str.contains(valor, case=False, na=False)]
            else:
                df_filtrado = df_filtrado[df_filtrado[columna] == valor]

    if df_filtrado.empty:
        return {"error": "Sin datos para estos filtros", "registros": 0}

    # 2. SEPARACIÓN POR AÑO (Análisis Comparativo)
    df_2025 = df_filtrado[df_filtrado['Mes, Año de fecha_liquidacion'].str.contains('2025', na=False)]
    df_2026 = df_filtrado[df_filtrado['Mes, Año de fecha_liquidacion'].str.contains('2026', na=False)]

    vn_2025 = round(df_2025['VN'].sum(), 2)
    vn_2026 = round(df_2026['VN'].sum(), 2)
    
    # Cálculo de variación porcentual
    variacion = 0
    if vn_2025 > 0:
        variacion = round(((vn_2026 - vn_2025) / vn_2025) * 100, 2)

    # 3. EXTRACCIÓN DE INSIGHTS (Análisis profundo)
    def obtener_insights(d_frame):
        if d_frame.empty: return None
        # Día de más ventas
        top_dia = d_frame.groupby('Día de fecha_liquidacion')['VN'].sum().idxmax()
        # Mejor cliente
        top_cliente = d_frame.groupby('nomb_cliente')['VN'].sum().idxmax()
        # Marca líder (en caso de que el filtro sea por región/cliente)
        top_marca = d_frame.groupby('desc_marca')['VN'].sum().idxmax()
        return {
            "dia_pico": int(top_dia),
            "cliente_estrella": top_cliente,
            "marca_lider": top_marca
        }

    return {
        "status": "success",
        "comparativo_anual": {
            "venta_2025": vn_2025,
            "venta_2026": vn_2026,
            "variacion_porcentual": f"{variacion}%",
            "estado": "Crecimiento" if variacion > 0 else "Caída"
        },
        "analisis_detallado_2026": obtener_insights(df_2026),
        "analisis_detallado_2025": obtener_insights(df_2025),
        "contexto_adicional": {
            "unidades_totales_2026": int(df_2026['Vol'].sum()),
            "regiones_activas": df_filtrado['Region'].unique().tolist()
        },
        "filtros_usados": {k: v for k, v in filtros.items() if v is not None}
    }
