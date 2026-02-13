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

# gb.configure_selection("multiple")
gb.configure_selection(
    selection_mode="single",
    # selection_mode="multiple",
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




# st.title("Simulación Tree (Community)")

# # -----------------------------
# # Datos base jerárquicos
# # -----------------------------
# data = [
#     {"tipo": "padre", "id": 1, "parent": None, "nombre": "Pedido 1001"},
#     {"tipo": "hijo", "id": 2, "parent": 1, "nombre": "Producto A"},
#     {"tipo": "hijo", "id": 3, "parent": 1, "nombre": "Producto B"},
#     {"tipo": "padre", "id": 4, "parent": None, "nombre": "Pedido 1002"},
#     {"tipo": "hijo", "id": 5, "parent": 4, "nombre": "Producto C"},
# ]

# df_base = pd.DataFrame(data)

# # -----------------------------
# # Estado expandido
# # -----------------------------
# if "expanded" not in st.session_state:
#     st.session_state.expanded = set()

# # -----------------------------
# # Construir dataframe visible
# # -----------------------------
# rows = []

# for _, row in df_base.iterrows():
#     if row["tipo"] == "padre":
#         is_expanded = row["id"] in st.session_state.expanded
#         icon = "🔽" if is_expanded else "▶"

#         rows.append({
#             "tree": f"{icon} {row['nombre']}",
#             "id": row["id"],
#             "tipo": "padre"
#         })

#         if is_expanded:
#             children = df_base[df_base["parent"] == row["id"]]
#             for _, child in children.iterrows():
#                 rows.append({
#                     "tree": f"    ↳ {child['nombre']}",
#                     "id": child["id"],
#                     "tipo": "hijo"
#                 })

# df = pd.DataFrame(rows)

# # -----------------------------
# # Configurar grid
# # -----------------------------
# gb = GridOptionsBuilder.from_dataframe(df)

# gb.configure_default_column(resizable=True)

# # Estilo padres en negrita
# cell_style = JsCode("""
# function(params) {
#     if (params.data.tipo === 'padre') {
#         return {fontWeight: 'bold'};
#     }
# }
# """)

# gb.configure_column("tree", headerName="Pedidos", cellStyle=cell_style)

# gb.configure_selection(
#     selection_mode="single",
#     use_checkbox=True
# )

# gb.configure_grid_options(
#     rowSelection="single",
#     suppressRowClickSelection=True,
#     enableRangeSelection=True
# )

# gridOptions = gb.build()

# grid_response = AgGrid(
#     df,
#     gridOptions=gridOptions,
#     allow_unsafe_jscode=True,
#     fit_columns_on_grid_load=True
# )

# # -----------------------------
# # Detectar click en padre
# # -----------------------------
# selected = grid_response.get("selected_rows")

# if isinstance(selected, pd.DataFrame) and not selected.empty:
#     selected_row = selected.iloc[0].to_dict()

#     if selected_row["tipo"] == "padre":
#         parent_id = selected_row["id"]

#         if parent_id in st.session_state.expanded:
#             st.session_state.expanded.remove(parent_id)
#         else:
#             st.session_state.expanded.add(parent_id)

#         st.rerun()

