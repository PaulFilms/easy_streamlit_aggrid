import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import json

# Datos
df = pd.DataFrame({
    "item": ["A", "B", "C", "D", "E"],
    "type": ["Tech", "Tech", "Hogar", "Hogar", "Tech"],
    "price": [100, 200, 150, 300, 250],
    "quantity": [5, 3, 8, 2, 6],
})

# Construir grid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(filter=True)
gb.configure_column("quantity", filter="agNumberColumnFilter")  # ⚡ importante para filtros numéricos

gridOptions = gb.build()

# Filtro inicial
initial_filters = {
    "quantity": {
        "filterType": "number",
        "type": "equals",
        "filter": 5
    }
}

# Aplicar filtro en el grid, no en el dataframe
gridOptions["onGridReady"] = f"""
function(params) {{
    params.api.setFilterModel({json.dumps(initial_filters)});
    params.api.onFilterChanged();
}}
"""

# Mostrar grid completo, con filtros iniciales aplicados
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True
)