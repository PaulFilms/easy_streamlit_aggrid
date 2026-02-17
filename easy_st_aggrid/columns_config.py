'''
Toolkit to create 'columnDefs' in a more pythonist way

Columns
-------
col_base
col_text
col_date
col_checkbox

Style
-----
cell_style

Table
-----
easy_table
'''
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, Union, List, Tuple, Dict, Any, Literal, TYPE_CHECKING

from st_aggrid import AgGrid, JsCode, GridOptionsBuilder, ColumnsAutoSizeMode
# from icons import *

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class cell_style:
    '''
    Minimun parameters to config the cell style

    Parameters
    ----------
    fontSize : int
    fontFamily : str
    fontWeight : "bold" or None
    color: str ("#000000")
    '''
    fontSize: Optional[int] = 15
    fontFamily: Optional[str] = "Neo Sans, sans-serif"
    fontWeight: Optional[str] = None
    color: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        cell_dict = dict()
        for k, v in asdict(self).items():
            if v != None:
                cell_dict[k] = v
        if cell_dict.get('fontSize'):
            cell_dict['fontSize'] = f"{self.fontSize}px"
        cell_dict['display'] = "flex"
        cell_dict['paddingLeft'] = "20px"
        cell_dict['alignItems'] = "center" # "center" | "top" | "bottom"
        return cell_dict

default_cell = cell_style(
    fontSize=14,
)

default_header = cell_style(
    fontSize=15,
    fontWeight="bold",
)


## FIELDS

@dataclass
class col_base:
    '''
    Base object to define a column of AgGrid table

    Parameters
    ----------
    id : str or None
    alias : str or None
    filter : bool or None
    width : int or None
    minWidth : int or None
    maxWidth : int or None
    pinned : "left", "right", bool or None
    headerStyle : Dict[str, Any] or None
    cellStyle : Dict[str, Any] or None
    columnGroupShow : "open", "closed" or None
    children : List[col_base] or None
    kwargs : Dict[str, Any]

    Methods
    -------
    data
    '''
    id: Optional[str] = None
    alias: Optional[str] = None
    filter: Union[bool, str, None] = True
    width: Optional[int] = None
    minWidth: Optional[int] = None
    maxWidth: Optional[int] = None
    # pinned: Literal["left", "right", False] = False
    pinned: bool = False
    headerStyle: Optional[Dict[str, Any]] = None
    cellStyle: Optional[Dict[str, Any]] = None

    columnGroupShow: Union[bool, str, None] = None
    children: Optional[List['col_base']] = None
    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)
    

    def data(self) -> Dict[str, Any]:
        '''
        Returns a dictionary key, value from defined objects
        '''
        col_options = dict()

        col_options['field'] = self.id
        if self.alias != None:
            col_options["headerName"] = self.alias
        
        if not self.filter:
            col_options['filter'] = False
        else:
            col_options['filter'] = True
        if isinstance(self.filter, str):
            col_options['filter'] = self.filter

        if self.width != None:
            # col_options['width'] = self.width
            # col_options["suppressSizeToFit"] = True # evita autosize wrapper
            # col_options.pop("flex", None) # evita flex accidental
            # col_options["flex"] = 0
            col_options.update({
                "width": self.width,
                "flex": 0,
                "suppressSizeToFit": True,
            })
        if self.minWidth != None:
            col_options['minWidth'] = self.minWidth
        if self.maxWidth != None:
            col_options['maxWidth'] = self.maxWidth
        if self.pinned:
            # col_options['pinned'] = 'left'
            col_options['pinned'] = 'true'
        if self.columnGroupShow:
            col_options['columnGroupShow'] = self.columnGroupShow
        if self.children:
            # col_options['children'] = self.children
            col_options['children'] = [child.data() for child in self.children]

        if self.headerStyle != None:
            col_options['headerStyle'] = self.headerStyle
        else:
            col_options['headerStyle'] = default_header.to_dict()
        if self.cellStyle != None:
            col_options['cellStyle'] = self.cellStyle
        else:
            col_options['cellStyle'] = default_cell.to_dict()
        
        for k, v in self.kwargs.items():
            col_options[k] = v
        
        return col_options

@dataclass
class col_text(col_base):
    '''
    Text column
    '''
    def __post_init__(self):
        if self.filter:
            self.filter = 'agTextColumnFilter'

@dataclass
class col_date(col_base):
    '''
    Date column (YYYY-MM-DD)
    '''

    def __post_init__(self):
        # if self.filter:
            ## Se opta por agTextColumnFilter en vez de agDateColumnFilter por simplicidad
            # self.filter = "agDateColumnFilter", "filterParams": {"customFormatString": "yyyy-MM-dd", "browserDatePicker": True, "comparator": comparator}, 
            # self.filter = 'agTextColumnFilter'
        
        # value_formatter_js = JsCode("""
        #     function(params) {
        #         if (params.value) {
        #             const date = new Date(params.value);
        #             const year = date.getFullYear();
        #             const month = ('0' + (date.getMonth() + 1)).slice(-2);
        #             const day = ('0' + date.getDate()).slice(-2);
        #             return year + '-' + month + '-' + day;
        #         } else {
        #             return '';
        #         }
        #     }
        # """)

        value_formatter_js = JsCode("""
        function (params) {
            const v = params.value;

            // Null, undefined, empty string
            if (v === null || v === undefined || v === '') {
                return '';
            }

            const date = new Date(v);

            // Fecha inválida
            if (isNaN(date.getTime())) {
                return '';
            }

            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');

            return `${year}-${month}-${day}`;
        }
        """)

        self.kwargs.update({
            "filterParams": {"customFormatString": "yyyy-MM-dd"},
            "type": ["agTextColumnFilter", "customDateTimeFormat"],
            "valueFormatter": value_formatter_js,
        })

@dataclass
class col_checkbox(col_base):
    '''
    Checkbox column
    '''

    def __post_init__(self):
        self.filter = False
        self.width = 40
        self.maxWidth = 40
        self.minWidth = 40
        self.kwargs.update({
            "checkboxSelection": True,
            "headerCheckboxSelection": True,  # checkbox en el header para seleccionar todo
            "pinned": "left",
            "sortable": True,
            "resizable": False,
        })


from dataclasses import dataclass, field
from typing import List
import json
from st_aggrid import JsCode


@dataclass
class col_status(col_base):
    """
    Strict status column:
    - Requires explicit states
    - No defaults allowed
    - CSS generated from Python
    - Renderer minimal & efficient
    """

    states: List["col_status.state"] = field(default_factory=list)

    def __post_init__(self):

        # -------- VALIDACIÓN --------
        if not self.states:
            raise ValueError(
                "col_status requires a non-empty 'states' list."
            )

        ids = set()
        for s in self.states:

            if s.id is None:
                raise ValueError("State id cannot be None.")

            if s.id in ids:
                raise ValueError(f"Duplicate state id detected: {s.id}")

            if not s.alias:
                raise ValueError(f"State alias cannot be empty (id={s.id}).")

            if not s.color:
                raise ValueError(f"State color cannot be empty (id={s.id}).")

            ids.add(s.id)

        # -------- FILTRO --------
        if self.filter:
            self.filter = "agSetColumnFilter"

        # -------- MAPA SERIALIZABLE --------
        status_map = {
            str(s.id): {
                "alias": s.alias,
                "color": s.color
            }
            for s in self.states
        }

        status_map_js = json.dumps(status_map)

        # -------- GENERACIÓN CSS DESDE PYTHON --------
        css = """
        .status-badge {
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding:4px 10px;
            border-radius:12px;
            font-weight:600;
            font-size:12px;
        }

        .status-dot {
            position:relative;
            width:8px;
            height:8px;
            flex-shrink:0;
        }

        .status-dot::before {
            content:'';
            position:absolute;
            width:8px;
            height:8px;
            border-radius:50%;
            top:0;
            left:0;
        }

        .status-dot::after {
            content:'';
            position:absolute;
            top:-3px;
            left:-3px;
            width:14px;
            height:14px;
            border-radius:50%;
            opacity:0;
            animation: status_pulse 2s ease-out infinite;
        }

        @keyframes status_pulse {
            0% { opacity:.6; transform:scale(.7); }
            100% { opacity:0; transform:scale(2); }
        }
        """

        for s in self.states:
            color = s.color

            # expandir hex corto
            if len(color) == 4 and color.startswith("#"):
                color = "#" + "".join(c*2 for c in color[1:])

            css += f"""
            .status-{s.id} {{
                background:{color}22;
                color:{color};
            }}

            .status-{s.id} .status-dot::before {{
                background:{color};
            }}

            .status-{s.id} .status-dot::after {{
                border:1.5px solid {color};
            }}
            """

        css_js = json.dumps(css)

        # -------- RENDERER MINIMAL --------
        _STATUS_RENDERER = JsCode(f"""
        class StatusRenderer {{
            init(params) {{

                const map = {status_map_js};
                const val = String(params.value ?? "");
                const entry = map[val];

                if (!entry) {{
                    this.eGui = document.createElement('span');
                    return;
                }}

                // Inyectar CSS una sola vez
                if (!window.__status_css__) {{
                    const style = document.createElement('style');
                    style.innerHTML = {css_js};
                    document.head.appendChild(style);
                    window.__status_css__ = true;
                }}

                this.eGui = document.createElement('span');
                this.eGui.className = "status-badge status-" + val;

                const txt = document.createElement('span');
                txt.textContent = entry.alias;

                const dot = document.createElement('div');
                dot.className = "status-dot";

                this.eGui.appendChild(txt);
                this.eGui.appendChild(dot);
            }}

            getGui() {{
                return this.eGui;
            }}
        }}
        """)

        # -------- FORMATTER PARA FILTRO --------
        _VALUE_FORMATTER = JsCode(f"""
            function(params) {{
                const map = {status_map_js};
                const val = String(params.value ?? "");
                const entry = map[val];
                return entry ? entry.alias : "";
            }}
        """)

        self.kwargs.update({
            "cellRenderer": _STATUS_RENDERER,
            "valueFormatter": _VALUE_FORMATTER,
            "filterParams": {
                "valueFormatter": _VALUE_FORMATTER
            }
        })

    # -------- CLASE STATE --------
    @dataclass
    class state:
        id: int
        alias: str
        color: str

## TABLE

def _columns_config(columns_list: List[col_base]) -> List[Dict]:
    '''
    Returns a list of dicts to be used in AgGrid columnDefs
    '''
    # Recibe una lista de objetos col_base y devuelve lista de dicts
    return [col.data() for col in columns_list]

def easy_table(
        dataframe: 'pd.DataFrame', 
        columns_list: List[col_base] = None, 
        cell_style: cell_style = default_cell, 
        getRowStyle: str = None,
        select_checkbox: bool = True,
        fit_columns_on_grid_load: bool = False,
        height: int = None,
        row_height: int = 40,
        floatingFilter: bool = False,
        # statusbar: bool = False,
        sidebar: bool = False,
    ): #  -> Any | str | 'pd.DataFrame' | None
    '''
    Render a dataframe with AgGrid and custom options
    '''

    ## DATAFRAME
    df = dataframe.copy()
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
        # floatingFilter=False,
    )
    
    gb.configure_selection(
        selection_mode="single",
        # selection_mode="multiple",
        use_checkbox=True
    )

    statusBar_enterprise = {
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

    # Configuraciones por defecto
    gb.configure_grid_options( # Aqui los defaults
        statusBar=statusBar_enterprise,
        rowSelection="single",          # IMPORTANTE
        # rowSelection="multiple",          # IMPORTANTE
        enableRangeSelection=True,        # Para copiar rango
        enableCellTextSelection=False,    # <- CLAVE en Mac
        suppressRowClickSelection=True,    # evita conflicto foco
        suppressMovableColumns=True, # Bloquear reordenar columnas
        supressSizeToFit=True,
        suppressColumnVirtualisation=True,
        rowHeight = row_height, # Definir altura fija de filas
        # defaultColDef={
        #     "wrapText": False, # grid_options['defaultColDef']['wrapText'] = True
        #     "autoHeight": False, # grid_options['defaultColDef']['autoHeight'] = True
        # },
    )

    grid_options = gb.build()

    grid_options['defaultColDef']["cellStyle"] = cell_style.to_dict()
    # grid_options['getRowStyle'] = row_style_js  # gb.configure_grid_options(getRowStyle=row_style_js)
    
    # if getRowStyle:
    #     grid_options['getRowStyle'] = JsCode(getRowStyle)
    
    if columns_list:
        grid_options['columnDefs'] = _columns_config(columns_list=columns_list) #  or col.children

        if select_checkbox:
            grid_options['columnDefs'].insert(0, {
                "headerName": "",
                "field": "__selection__",
                "checkboxSelection": True,
                "headerCheckboxSelection": False,
                "width": 40,
                "maxWidth": 40,
                "minWidth": 40,
                "pinned": "left",
                "sortable": False,
                "resizable": False,
                "filter": False,

                "cellStyle": {
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",   # centra horizontal
                    "padding": "0"                # elimina padding
                }
            })

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
                # {
                #     "id": "filters",
                #     "labelDefault": "Filtros",
                #     "iconKey": "filter",
                #     "toolPanel": "agFiltersToolPanel"
                # }
            ],
            # "defaultToolPanel": "columns" # No poner para que renderice cerrada
            # "defaultToolPanel": None
        }


    ## TABLE
    response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,  # necesario para aggregation
        allow_unsafe_jscode=True,
        height=height,  # opcional, ignora alto fijo
        fit_columns_on_grid_load = fit_columns_on_grid_load,
        # columns_auto_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        columns_auto_size_mode = "FIT_ALL_COLUMNS_TO_VIEW",
        # domLayout="autoHeight",
        theme='streamlit'
    )

    return response.selected_data