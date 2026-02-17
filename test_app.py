import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.title("Ejemplo Status Bar - AG Grid")

# Datos de ejemplo
df = pd.DataFrame({
    "Producto": ["A", "B", "C", "D", "E"],
    "Categoria": ["Tech", "Tech", "Hogar", "Hogar", "Tech"],
    "Precio": [100, 200, 150, 300, 250],
    "Cantidad": [5, 3, 8, 2, 6],
    "fecha": ["2026-01-01","2026-02-01","2026-03-01","2026-04-01","2026-05-01",]
})

# Construir grid
gb = GridOptionsBuilder.from_dataframe(df)

# Activar filtros, ordenación y selección
gb.configure_default_column(
    filter=True,
    sortable=True,
    resizable=True,
    editable=False,
    # floatingFilter=True
)

# 🔥 Activar Side Bar
# gb.configure_grid_options(
#     sideBar=True,  # 👈 esto ya activa Columns + Filters
#     enableRangeSelection=True
# )


gb.configure_selection(
    selection_mode="single",
    use_checkbox=True
)

# Checkbox en primera columna
first_col = df.columns[0]

gb.configure_column(
    first_col,
    checkboxSelection=True,
    headerCheckboxSelection=True
)

statusBar_enterprise={
    "statusPanels": [
        # 🟢 GRATIS
        {
            "statusPanel": "agTotalRowCountComponent",
            "align": "left"
        },
        {
            "statusPanel": "agFilteredRowCountComponent",
            # "align": "left"
        },
        {
            "statusPanel": "agSelectedRowCountComponent"
        },
        # 🔵 ENTERPRISE
        {
            "statusPanel": "agAggregationComponent"
        }
    ]
}

statusBar_free = {
    "statusPanels": [
        {"statusPanel": "agTotalRowCountComponent"},
        {"statusPanel": "agFilteredRowCountComponent"},
        {"statusPanel": "agSelectedRowCountComponent"}
    ]
}

# 🔹 Configuración de Status Bar
gb.configure_grid_options(
    statusBar=statusBar_enterprise,
    rowSelection="single",          # IMPORTANTE
    # rowSelection="multiple",          # IMPORTANTE
    enableRangeSelection=True,        # Para copiar rango
    enableCellTextSelection=False,    # <- CLAVE en Mac
    suppressRowClickSelection=True,    # evita conflicto foco
    # 
    sideBar={
        "toolPanels": [
            {
                "id": "columns",
                "labelDefault": "Columnas",
                "iconKey": "columns",
                "toolPanel": "agColumnsToolPanel"
            },
            {
                "id": "filters",
                "labelDefault": "Filtros",
                "iconKey": "filter",
                "toolPanel": "agFiltersToolPanel"
            }
        ],
        # "defaultToolPanel": "columns" # No poner para que renderice cerrada
    }
)

gridOptions = gb.build()

AgGrid(
    df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,  # necesario para aggregation
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True
)

st.text_area('testo')

