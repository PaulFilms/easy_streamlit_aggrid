# __all__ = ['easy_table']

from typing import Literal, Optional, List, Dict
from enum import Enum
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import StAggridTheme
from easy_st_aggrid.defaults import *
# from easy_st_aggrid.co

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

# def _columns_config(columns_list: List[col_base]) -> List[Dict]:
#     '''
#     Returns a list of dicts to be used in AgGrid columnDefs
#     '''
#     return [col.data() for col in columns_list]

def _extract_fields(column_defs, exclude_prefix="__"):
    """
    Recorre recursivamente columnDefs (con cualquier nivel de children)
    y devuelve todos los field exportables respetando el orden visual.
    """

    fields = []

    for col in column_defs:

        # Caso 1: es un grupo
        if isinstance(col, dict) and "children" in col:
            fields.extend(
                _extract_fields(col["children"], exclude_prefix)
            )

        # Caso 2: es columna normal
        else:
            field = col.get("field")

            if (
                field
                and not field.startswith(exclude_prefix)
            ):
                fields.append(field)

    return fields

# class Theme(str, Enum):
#     STREAMLIT = "streamlit"
#     LIGHT = "light"
#     DARK = "dark"

def build_column_defs(df, columns_list: Optional[List[col_base]] = None) -> List[Dict]:
    # Sin configuracion custom: todas las columnas planas del dataframe
    if not columns_list:
        return [
            {
                "field": col_name,
                "headerTooltip": col_name,
            }
            for col_name in df.columns
        ]

    # Con configuracion custom: respetar jerarquia (children) y orden definidos
    column_defs = [col.data() for col in columns_list]

    # Mantener compatibilidad: anadir al final columnas del df no configuradas
    configured_ids = set(_extract_fields(column_defs))
    for col_name in df.columns:
        if col_name not in configured_ids:
            column_defs.append(
                {
                    "field": col_name,
                    "headerTooltip": col_name,
                }
            )

    return column_defs

def easy_table(
        dataframe: 'pd.DataFrame', 
        columns_list: List[col_base] = None, 
        cell_style: cell_style = default_cell,
        header_style: cell_style = default_header,
        # getRowStyle: str = None,
        select_checkbox: bool = False,
        selection_multiple: bool = False,
        
        fit_columns_on_grid_load: bool = True,
        suppressMovableColumns: bool = True,
        floatingFilter: bool = False,
        statusbar: bool = False,
        sidebar: bool = False,

        height: int = None,
        row_height: int = 30,
        row_grouping: bool = False,
        # dark_theme: bool = False,
        # theme: Theme = Theme.STREAMLIT,
        theme: Literal["streamlit", "light", "dark"] = 'streamlit',

        #TREE DATA:
        # tree_data: bool = False,
        # tree_level_col: str = None,
        
        enterprise: bool = False,
    ): #  -> Any | str | 'pd.DataFrame' | None
    '''
    Render a dataframe with AgGrid and custom options

    Returns:
        response.selected_rows
    '''

    ## DATAFRAME
    df = dataframe.copy()

    # ---------------------------------------------------------------
    #  AUTO-CALCULAR maxAbs PARA col_bar (búsqueda recursiva)
    # ---------------------------------------------------------------


    # if columns_list:
    #     for col in _find_col_bars(columns_list):
    #         if col.max_abs is None and col.id in df.columns:
    #             series = pd.to_numeric(df[col.id], errors='coerce')
    #             max_val = series.abs().max()
    #             col.max_abs = float(max_val) if pd.notna(max_val) and max_val > 0 else 1
    #             col._build_renderer()
    # ---------------------------------------------------------------

    gb = GridOptionsBuilder.from_dataframe(df)

    # gb.configure_side_bar(
    #     filters_panel=True,
    #     columns_panel=True,
    # )

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        editable=False,
        floatingFilter=floatingFilter,
    )
    
    gb.configure_selection(
        # selection_mode="multiple" if selection_multiple else "single", # single / multiple
        # use_checkbox=select_checkbox,
        header_checkbox=selection_multiple
    )

    # DEFAULT CONFIG
    gb.configure_grid_options(
        rowSelection="multiple" if selection_multiple else "single", # single / multiple
        suppressRowClickSelection=True,    # evita conflicto foco
        enableRangeSelection=True,        # Para copiar rango
        enableCellTextSelection=False,    # <- CLAVE en MacOS
        suppressMovableColumns = suppressMovableColumns, # Bloquear reordenar columnas
        supressSizeToFit=True,
        suppressColumnVirtualisation=True,
        rowHeight = row_height,

        #PARA EXPORTAR A EXCEL:
        excelStyles=[
            {
                "id": "stringType",
                "dataType": "String",
            }
        ],
        # defaultColDef={
        #     "wrapText": False, # grid_options['defaultColDef']['wrapText'] = True
        #     "autoHeight": False, # grid_options['defaultColDef']['autoHeight'] = True
        # },
    )

    # ---------------------------------------------------------------
    #  ROW GROUPING 
    #----------------------------------------------------------------
    #De momento HARD-CODED:
    #1.Cuando se ve el menu superior para agrupar:
    # row_group_panel = "always"  #["never", "always", "onlyWhenGrouping"]

    # #2.Hasta qué nivel aparece expandido por defecto:
    #     #  0 = todo colapsado; 
    #     #  1 = Se abre el primer nivel
    #     #  -1 = Todo expandido
    # group_default_expanded: int = -1

    # #3.Nombre de la columna agrupacion:
    # # auto_group_name = "Agrupacion"

    # #4.Ancho de la columna agrupacion:
    # auto_group_width = 320

    # if row_grouping:
    #     gb.configure_grid_options(
    #         animateRows=True,
    #         groupDefaultExpanded=group_default_expanded,
    #         rowGroupPanelShow=row_group_panel,
    #         showOpenedGroup=True,
    #         suppressAggFuncInHeader=False,
    #         autoGroupColumnDef={
    #             "headerName": auto_group_name,
    #             "width": auto_group_width,
    #             "suppressSizeToFit": True, #PARA QUE NO SE AJUSTE
    #             # "pinned": "left", #ESTE PINNED NO SE PONE, porque al ponerlo la columna de agrupacion se pone mas a la izda que el checkbox ->FEO
    #             "cellRendererParams": {"suppressCount": False},
    #             "cellStyle": cell_style.to_dict(),
    #         },
    #     )


    # ---------------------------------------------------------------
    #  TREE DATA
    #----------------------------------------------------------------
    #Nombre y ancho de la columna agrupada (de momento HARD-CODED)
    auto_tree_name = "Nivel"
    auto_tree_width = 60


    # if tree_data:
    #     if not tree_level_col:
    #         raise ValueError("tree_data requires tree_level_col and tree_id_col")
    #     df = build_hierarchy(df, col_name=tree_level_col)
        
    #     gb.configure_grid_options(
    #         treeData=True,
    #         animateRows=True,
    #         getDataPath=JsCode("function(data) { return JSON.parse(data.hierarchy); }"),
    #         groupDefaultExpanded=group_default_expanded,
    #         autoGroupColumnDef={
    #             "headerName": auto_tree_name,
    #             "field": tree_level_col,
    #             "width": auto_tree_width,
    #             "suppressSizeToFit": True, #PARA QUE NO SE AJUSTE
    #             # "pinned": "left", #ESTE PINNED NO SE PONE, porque al ponerlo la columna de agrupacion se pone mas a la izda que el checkbox ->FEO
    #             "cellRendererParams": {"suppressCount": True},
    #             "cellStyle": cell_style.to_dict(),
    #         },
    #     )

    grid_options = gb.build()

    # 🔥 Forzar selección correctamente en 1.1.9
    # grid_options["rowSelection"] = "single"

    ## DEFAULT STYLE
    grid_options['defaultColDef']["headerStyle"] = header_style.to_dict()
    grid_options['defaultColDef']["cellStyle"] = cell_style.to_dict()

    # Ag-Grid aplica estilos de grupos en defaultColGroupDef, no en defaultColDef.
    # Esto mantiene font-size/font-weight consistentes entre headers normales y de grupo.
    grid_options.setdefault("defaultColGroupDef", {})
    grid_options["defaultColGroupDef"]["headerStyle"] = header_style.to_dict()
    # grid_options['getRowStyle'] = row_style_js  # gb.configure_grid_options(getRowStyle=row_style_js)
    
    # if getRowStyle:
    #     grid_options['getRowStyle'] = JsCode(getRowStyle)


    # grid_options["columnDefs"][0].update({
    #     "width": 100,
    #     "maxWidth": 40,
    #     "minWidth": 40,
    #     "pinned": "left",
    #     "sortable": False,
    #     "resizable": False,
    #     "filter": False
    # })

    ## STATUSBAR
    if statusbar:
        statusBar_enterprise = {
            "statusPanels": [
                # 🟢 GRATIS
                {"statusPanel": "agTotalRowCountComponent", "align": "left"},
                {"statusPanel": "agFilteredRowCountComponent",}, # "align": "left"},
                {"statusPanel": "agSelectedRowCountComponent"},
                # 🔵 ENTERPRISE
                {"statusPanel": "agAggregationComponent"}
            ]
        }
        statusBar_free = {
            "statusPanels": [
                {"statusPanel": "agTotalRowCountComponent"},
                {"statusPanel": "agFilteredRowCountComponent"},
                {"statusPanel": "agSelectedRowCountComponent"}
            ]
        }
        grid_options['statusBar'] = statusBar_enterprise

    ## SIDEBAR
    if sidebar:
        grid_options['sideBar'] = {
            "toolPanels": [
                {
                    "id": "columns",
                    "labelDefault": "Columnas",
                    "iconKey": "columns",
                    "toolPanel": "agColumnsToolPanel",
                    "toolPanelParams": {
                        "suppressRowGroups": True,
                        "suppressValues": True,
                        "suppressPivots": True,
                        "suppressPivotMode": True,
                        # opcionales extra:
                        # "suppressColumnFilter": True,
                        # "suppressColumnSelectAll": True,
                        # "suppressColumnExpandAll": True,
                        },
                },
                {
                    "id": "filters",
                    "labelDefault": "Filtros",
                    "iconKey": "filter",
                    "toolPanel": "agFiltersToolPanel"
                }
            ],
            # "defaultToolPanel": "columns" # No poner para que renderice cerrada
            # "defaultToolPanel": None
        }

    ## COLUMNS CONFIG LIST
    if columns_list:
        # grid_options['columnDefs'] = _columns_config(columns_list=columns_list) #  or col.children
        grid_options['columnDefs'] = build_column_defs(df, columns_list)

    ## CHECKBOX
    if select_checkbox:
        grid_options['columnDefs'].insert(0, {
            "headerName": "",
            "field": "__selection__",
            "checkboxSelection": True,
            "headerCheckboxSelection": selection_multiple,
            "headerCheckboxSelectionFilteredOnly": selection_multiple,
            "width": 50,
            "maxWidth": 50,
            "minWidth": 50,
            "pinned": "left",
            "sortable": False,
            "resizable": False,
            "filter": False,
            "suppressCsvExport": True,
            "suppressExcelExport": True,

            "cellStyle": {
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",   # centra horizontal
                "padding": "0"                # elimina padding
            }
        })


    exportable_columns = _extract_fields(grid_options["columnDefs"])
    grid_options["defaultExcelExportParams"] = {
        "columnKeys": exportable_columns,
    }
    grid_options["excelStyles"] = [
        {
            "id": "leftAlign",
            "alignment": {"horizontal": "Left"}
        }
    ]

    ## ROW GROUPING
    if (row_grouping and len(columns_list) > 1 and sum(1 for x in columns_list if x.enableRowGroup) > 0):
        grid_options['animateRows'] = True
        grid_options['groupDefaultExpanded'] = 0 # 0 = todo colapsado / 1 = Se abre el primer nivel / -1 = Todo expandido (nivel aparece expandido por defecto)
        grid_options['rowGroupPanelShow'] = 'always' # never / always / onlyWhenGrouping (Cuando se ve el menu superior para agrupar)
        grid_options['showOpenedGroup'] = True
        grid_options['suppressAggFuncInHeader'] = False
        grid_options['autoGroupColumnDef'] = {
            "headerName": 'Agrupacion', # Nombre de la columna agrupacion
            "width": 320,
            "suppressSizeToFit": True, #PARA QUE NO SE AJUSTE
            # "pinned": "left", #ESTE PINNED NO SE PONE, porque al ponerlo la columna de agrupacion se pone mas a la izda que el checkbox ->FEO
            "cellRendererParams": {"suppressCount": False},
            "cellStyle": cell_style.to_dict(),
        }


    # ---------------------------------------------------------------
    #  TREE DATA
    #----------------------------------------------------------------
    #Nombre y ancho de la columna agrupada (de momento HARD-CODED)
    # auto_tree_name = "Nivel"
    # auto_tree_width = 60


    # if tree_data:
    #     if not tree_level_col:
    #         raise ValueError("tree_data requires tree_level_col and tree_id_col")
    #     df = build_hierarchy(df, level_col=tree_level_col)
        
    #     gb.configure_grid_options(
    #         treeData=True,
    #         animateRows=True,
    #         getDataPath=JsCode("function(data) { return JSON.parse(data.hierarchy); }"),
    #         groupDefaultExpanded=group_default_expanded,
    #         autoGroupColumnDef={
    #             "headerName": auto_tree_name,
    #             "field": tree_level_col,
    #             "width": auto_tree_width,
    #             "suppressSizeToFit": True, #PARA QUE NO SE AJUSTE
    #             # "pinned": "left", #ESTE PINNED NO SE PONE, porque al ponerlo la columna de agrupacion se pone mas a la izda que el checkbox ->FEO
    #             "cellRendererParams": {"suppressCount": False},
    #             "cellStyle": cell_style.to_dict(),
    #         },
    #     )

    # ---------------------------------------------------------------
    #  TREE DATA
    #----------------------------------------------------------------

    ## THEME

    # if dark_theme:
    # if theme == Theme.DARK:
    if theme == 'dark':
        _theme = StAggridTheme(base='alpine').withParams(
            backgroundColor="#3D3D3D",
            foregroundColor="#e8e8e8",
            headerBackgroundColor="#1E1E1E",
            headerTextColor="#e8e8e8",
            rowBorder={"color": "#2a2a2a"},
            oddRowBackgroundColor="#1A1A1A",
            borderColor="#2a2a2a",
            selectedRowBackgroundColor="rgba(255,191,0,0.25)",
            rowHoverColor="rgba(255,191,0,0.10)",
            accentColor="#FFBF00",
            rangeSelectionBorderColor="#FFBF00",
        )
    
    # elif theme == Theme.LIGHT:
    elif theme == 'light':
        _theme = StAggridTheme(base='alpine').withParams( # alpine / balham
            backgroundColor="#FFFFFF",
            foregroundColor="#000000",
            headerBackgroundColor="#f8f8f8",

            oddRowBackgroundColor="#fafafa",
            selectedRowBackgroundColor="rgba(0,68,103,0.20)",
            rowHoverColor="rgba(0,68,103,0.08)",
            accentColor="#004467",
            rangeSelectionBorderColor="#004467",
        )
    
    
    ## TABLE
    return AgGrid(
        data=df,
        gridOptions=grid_options,
        enable_enterprise_modules=enterprise,  # necesario para aggregation
        allow_unsafe_jscode=True,

        height=height,  # opcional, ignora alto fijo
        fit_columns_on_grid_load = fit_columns_on_grid_load,
        # columns_auto_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        columns_auto_size_mode = "FIT_ALL_COLUMNS_TO_VIEW",
        # domLayout="autoHeight",
        # theme='dark' if dark_theme else 'light',
        # theme=_theme if theme in [Theme.DARK, Theme.LIGHT] else 'streamlit',
        theme=_theme if theme in ['dark', 'light'] else 'streamlit', # streamlit / alpine / balham
    )

