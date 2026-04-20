from fastapi import FastAPI, Query
import pandas as pd
from typing import Optional

app = FastAPI()

# Carga con separador punto y coma
df = pd.read_csv('fuente.csv', sep=';')

# Limpieza robusta de números
for col in ['Vol', 'VN']:
    # Convertimos a string, quitamos comas y convertimos a float
    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

@app.get("/consultar")
def consultar(
    marca: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    cliente: Optional[str] = Query(None),
    dia: Optional[int] = Query(None)
):
    # Iniciamos con la base completa
    df_filtrado = df.copy()

    # Diccionario de filtros dinámicos (Columna en CSV : Valor recibido)
    filtros = {
        'desc_marca': marca,
        'Region': region,
        'nomb_cliente': cliente,
        'Día de fecha_liquidacion': dia
    }

    # Aplicamos cada filtro si existe
    for columna, valor in filtros.items():
        if valor is not None:
            if isinstance(valor, str):
                df_filtrado = df_filtrado[df_filtrado[columna].str.contains(valor, case=False, na=False)]
            else:
                df_filtrado = df_filtrado[df_filtrado[columna] == valor]

    if df_filtrado.empty:
        return {"error": "No se encontraron datos para los filtros aplicados", "filtros": filtros}

    # Respuesta enriquecida para que la IA tenga contexto
    return {
        "status": "success",
        "resumen": {
            "total_venta_neta": round(float(df_filtrado['VN'].sum()), 2),
            "total_unidades": int(df_filtrado['Vol'].sum()),
            "cantidad_registros": len(df_filtrado)
        },
        "top_marcas": df_filtrado.groupby('desc_marca')['VN'].sum().sort_values(ascending=False).head(3).to_dict(),
        "top_regiones": df_filtrado.groupby('Region')['VN'].sum().sort_values(ascending=False).to_dict(),
        "filtros_aplicados": {k: v for k, v in filtros.items() if v is not None}
    }
