import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.title("Ejemplo Status Bar - AG Grid")

# Datos de ejemplo
df = pd.DataFrame({
    "item": ["A", "B", "C", "D", "E"],
    "type": ["Tech", "Tech", "Hogar", "Hogar", "Tech"],
    "price": [100, 200, 150, 300, 250],
    "quantity": [5, 3, 8, 2, 6],
    "date": ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01",]
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

## TIMELINE
## _________________________________________________________________________________________________________________

df = pd.DataFrame({
    "Nombre": ["1", "A", "B", "C"],
    "inicio": [10, 20, 40, 10],
    "fin": [70, 50, 70, 60],
})

# MIN_GLOBAL = 0
# MAX_GLOBAL = 100
MIN_GLOBAL = df['inicio'].min()
MAX_GLOBAL = df['fin'].max()
RANGO = MAX_GLOBAL - MIN_GLOBAL

from st_aggrid import JsCode

cell_renderer = JsCode(f"""
class RangeBarRenderer {{
    init(params) {{
        const min = {MIN_GLOBAL};
        const max = {MAX_GLOBAL};
        const totalRange = max - min;

        const start = params.data.inicio;
        const end = params.data.fin;

        const startPercent = ((start - min) / totalRange) * 100;
        const widthPercent = ((end - start) / totalRange) * 100;

        this.eGui = document.createElement('div');
        this.eGui.style.position = 'relative';
        this.eGui.style.height = '20px';
        this.eGui.style.backgroundColor = '#eee';
        this.eGui.style.borderRadius = '4px';

        const bar = document.createElement('div');
        bar.style.position = 'absolute';
        bar.style.left = startPercent + '%';
        bar.style.width = widthPercent + '%';
        bar.style.height = '100%';
        bar.style.backgroundColor = '#4CAF50';
        bar.style.borderRadius = '4px';

        this.eGui.appendChild(bar);
    }}

    getGui() {{
        return this.eGui;
    }}
}}
""")

from st_aggrid import JsCode

cell_renderer = JsCode(f"""
class RangeBarRenderer {{
    init(params) {{
        const min = {MIN_GLOBAL};
        const max = {MAX_GLOBAL};
        const totalRange = max - min;

        const start = params.data.inicio;
        const end = params.data.fin;

        const startPercent = ((start - min) / totalRange) * 100;
        const widthPercent = ((end - start) / totalRange) * 100;

        // CONTENEDOR PRINCIPAL (centra vertical y horizontalmente)
        this.eGui = document.createElement('div');
        this.eGui.style.display = 'flex';
        this.eGui.style.alignItems = 'center';
        this.eGui.style.justifyContent = 'center';
        this.eGui.style.height = '100%';
        this.eGui.style.width = '100%';

        // BARRA DE FONDO (timeline completo)
        const background = document.createElement('div');
        background.style.position = 'relative';
        background.style.width = '95%';
        background.style.height = '40px';
        background.style.background = 'rgba(100, 100, 100, 0.3)';
        background.style.border = '2px solid rgba(70, 70, 70, 0.2)';
        background.style.borderRadius = '6px';
        background.style.boxSizing = 'border-box';

        // TEXTO MIN Y MAX
        const minLabel = document.createElement('span');
        minLabel.innerText = min;
        minLabel.style.position = 'absolute';
        minLabel.style.left = '8px';
        minLabel.style.top = '50%';
        minLabel.style.transform = 'translateY(-50%)';
        minLabel.style.fontSize = '12px';
        minLabel.style.color = '#000';

        const maxLabel = document.createElement('span');
        maxLabel.innerText = max;
        maxLabel.style.position = 'absolute';
        maxLabel.style.right = '8px';
        maxLabel.style.top = '50%';
        maxLabel.style.transform = 'translateY(-50%)';
        maxLabel.style.fontSize = '12px';
        maxLabel.style.color = '#000';

        // BARRA VERDE (rango activo)
        const bar = document.createElement('div');
        bar.style.position = 'absolute';
        bar.style.left = startPercent + '%';
        bar.style.width = widthPercent + '%';
        bar.style.height = '100%';
        bar.style.background = '#66D575';
        bar.style.border = '2px solid rgba(62,155,75,0.4)';
        bar.style.borderRadius = '6px';
        bar.style.boxSizing = 'border-box';
        bar.style.display = 'flex';
        bar.style.alignItems = 'center';
        bar.style.justifyContent = 'center';
        bar.style.fontSize = '14px';
        bar.style.fontWeight = '500';
        bar.style.color = 'rgba(0,0,0,0.4)';

        // bar.innerText = start + " - " + end;

        background.appendChild(bar);
        // background.appendChild(minLabel);
        // background.appendChild(maxLabel);

        this.eGui.appendChild(background);
    }}

    getGui() {{
        return this.eGui;
    }}
}}
""")

gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_column(
    "inicio",
    header_name="Rango",
    cellRenderer=cell_renderer,
)

gb.configure_grid_options(rowHeight=60)

grid_options = gb.build()

AgGrid(
    df,
    gridOptions=grid_options,
    height=300,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
)
