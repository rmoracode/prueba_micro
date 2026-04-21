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
    dia: Optional[str] = Query(None)  # Lo cambiamos a str para evitar el error 422
):
    df_filtrado = df.copy()

    # Procesamos el día solo si no está vacío y es un número
    dia_final = None
    if dia and dia.strip():
        try:
            dia_final = int(dia)
        except ValueError:
            pass # Si no es un número válido, lo ignoramos

    filtros = {
        'desc_marca': marca,
        'Region': region,
        'nomb_cliente': cliente,
        'Día de fecha_liquidacion': dia_final
    }

    for columna, valor in filtros.items():
        if valor is not None and str(valor).strip() != "":
            if isinstance(valor, str):
                df_filtrado = df_filtrado[df_filtrado[columna].str.contains(valor, case=False, na=False)]
            else:
                df_filtrado = df_filtrado[df_filtrado[columna] == valor]

    if df_filtrado.empty:
        return {"mensaje": "No se encontraron datos", "registros": 0}

    return {
        "status": "success",
        "resumen": {
            "total_venta_neta": round(float(df_filtrado['VN'].sum()), 2),
            "total_unidades": int(df_filtrado['Vol'].sum()),
            "cantidad_registros": len(df_filtrado)
        },
        "top_marcas": df_filtrado.groupby('desc_marca')['VN'].sum().sort_values(ascending=False).head(3).to_dict(),
        "filtros_aplicados": {k: v for k, v in filtros.items() if v is not None}
    }
