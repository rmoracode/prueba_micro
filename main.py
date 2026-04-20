from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI()

# Esto carga el archivo en memoria al arrancar para que sea instantáneo
df = pd.read_csv('fuente.csv', sep=';')
df['Vol'] = df['Vol'].astype(str).str.replace(',', '').astype(float)
df['VN'] = df['VN'].astype(str).str.replace(',', '').astype(float)

@app.get("/consultar")
def consultar(marca: str = Query(None)):
    if not marca:
        return {"error": "Debes pasar una marca, ej: /consultar?marca=CIFRUT"}
    
    # Buscamos la marca
    resultado = df[df['desc_marca'].str.contains(marca, case=False, na=False)]
    
    return {
        "marca": marca,
        "total_unidades": int(resultado['Vol'].sum()),
        "total_venta_neta": round(float(resultado['VN'].sum()), 2),
        "registros_encontrados": len(resultado)
    }
