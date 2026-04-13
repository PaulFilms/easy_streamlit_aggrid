# __all__ = [
#     'cell_style', 
#     'default_cell', 
#     'default_header', 
#     'col_base', 
#     'col_text', 
#     'col_bool',
#     'col_str_date',
# ]

from typing import Optional, Union, List, Tuple, Dict, Any, Literal, TYPE_CHECKING
from dataclasses import dataclass, asdict, field

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
import pandas as pd

from easy_st_aggrid import *

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
    background_color : int
    '''
    fontSize: Optional[int] = 13
    fontFamily: Optional[str] = "Neo Sans, sans-serif"
    fontWeight: Optional[str] = None
    color: Optional[str] = None
    background_color: Optional[str] = None

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
        if self.background_color:
            cell_dict['background-color'] = cell_dict.pop('background_color')
        return cell_dict

default_cell = cell_style(
    fontSize=14,
)

default_header = cell_style(
    fontSize=14,
    fontWeight="bold",
)



## COLUMNS TYPES
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
    cellStyle : Dict[str, Any] or None
    headerStyle : Dict[str, Any] or None
    headerTooltip: Optional[str] = None
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
    cellStyle: Optional[Dict[str, Any]] = None
    headerStyle: Optional[Dict[str, Any]] = None
    headerTooltip: Optional[str] = None

    columnGroupShow: Union[bool, str, None] = None
    children: Optional[List['col_base']] = None

    #ROW GROUPING:
    rowGroup: bool = False              # Agrupa filas por esta columna (ej: proyecto → solped)
    enableRowGroup: bool = False        # Permite al usuario arrastrarla al panel de agrupación

    # hide: bool = False                  # Oculta la columna (ya se ve en la columna de agrupación)
    # aggFunc: Optional[str] = None       # Función de agregación en filas grupo ("sum", "avg", etc.)
    # enableValue: bool = False           # Permite al usuario cambiar la aggregation desde el sidebar

    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def data(self) -> Dict[str, Any]:
        '''
        Returns a dictionary key, value from defined objects
        '''
        col_options = dict()

        if self.id is not None:
            col_options['field'] = self.id
            col_options["headerTooltip"] = self.id
        elif self.alias is not None:
            col_options["headerTooltip"] = self.alias

        if self.alias != None:
            col_options["headerName"] = self.alias
            col_options["headerTooltip"] = self.alias
        
        if not self.filter:
            col_options['filter'] = False
        else:
            col_options['filter'] = True
        if isinstance(self.filter, str):
            col_options['filter'] = self.filter

        if self.width != None:
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
        if self.headerTooltip is not None:
            col_options["headerTooltip"] = self.headerTooltip
        if self.columnGroupShow:
            col_options['columnGroupShow'] = self.columnGroupShow
        if self.children:
            col_options['children'] = [child.data() for child in self.children]

        # col_options['headerStyle'] = default_header.to_dict()
        if self.headerStyle:
            col_options['headerStyle'] = self.headerStyle.to_dict()

        # col_options['cellStyle'] = default_cell.to_dict()
        if self.cellStyle != None:
            col_options['cellStyle'] = self.cellStyle.to_dict()
            
        col_options['cellClass']="leftAlign"

        
        #ROW GROUPING:
        if self.rowGroup:
            col_options['rowGroup'] = True
        # if self.hide:
        #     col_options['hide'] = True
        # if self.aggFunc:
        #     col_options['aggFunc'] = self.aggFunc
        if self.enableRowGroup:
            col_options['enableRowGroup'] = True
        # if self.enableValue:
        #     col_options['enableValue'] = True
        
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
        # Exportar siempre como texto en Excel (evita notación científica)
        self.kwargs = dict(self.kwargs) if self.kwargs else {}
        self.kwargs.setdefault("cellClass", "stringType")

@dataclass
class col_bool(col_base):
    '''
    Boolean column configuration for AgGrid.

    Extends `col_base` to provide a user-friendly visualization of boolean
    values using custom rendering (e.g. emojis or labels).

    By default, boolean values are displayed as:
        True  → ✅
        False → ❌

    This behavior can be customized via the `values` parameter.

    Parameters
    ----------
    values : Dict[bool, str], optional
        Mapping used to render boolean values in the cell.
        If not provided, defaults to {True: "✅", False: "❌"}.

    filter : bool or str, optional
        Overrides default filter behavior. If True, uses 'agTextColumnFilter'.

    kwargs : Dict[str, Any], optional
        Additional AgGrid column definition properties.

    Behavior
    --------
    - Uses a custom `cellRenderer` to display boolean values.
    - Applies centered cell styling by default.
    - Supports null values (renders as empty string).
    - Can be extended to support export formatting.

    Examples
    --------
    Default usage:
        col_bool("activo")

    Custom labels:
        col_bool("activo", values={True: "SI", False: "NO"})

    Custom icons:
        col_bool("activo", values={True: "🟢", False: "🔴"})
    '''

    values: Optional[Dict[bool, str]] = None

    def __post_init__(self):
        if self.filter:
            self.filter = 'agTextColumnFilter' # agSetColumnFilter

        self.kwargs = dict(self.kwargs) if self.kwargs else {}

        # 👇 default mapping
        mapping = self.values or {
            True: '✅',
            False: '❌'
        }

        # 👇 construir JS dinámicamente
        js_renderer = f"""
        function(params) {{
            const value = params.value;

            if (value === true) return '{mapping.get(True, "")}';
            if (value === false) return '{mapping.get(False, "")}';
            return '';
        }}
        """

        self.kwargs["cellRenderer"] = JsCode(js_renderer)

        # Centrado
        self.kwargs["cellStyle"] = {
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "fontSize": "16px"
        }

@dataclass
class col_str_date(col_base):
    """
    Column for dates stored as strings (yyyy-mm-dd).

    Notes
    -----
    - The DataFrame must provide the column as string in 'yyyy-mm-dd' format.
    - Nulos should be None or empty string ''.
    - Uses SetColumnFilter to allow hierarchical filtering by year/month/day.
    """
    def __post_init__(self):
        self.filter = "agSetColumnFilter"
        self.kwargs = dict(self.kwargs) if self.kwargs else {}

        # Renderer: show empty for null, otherwise string
        self.kwargs["cellRenderer"] = JsCode("""
        function(params) {
            const val = params.value;
            if (!val) return '';
            return val;
        }
        """)

        # Center cell
        # self.kwargs["cellStyle"] = {
        #     "display": "flex",
        #     "justifyContent": "center",
        #     "alignItems": "center",
        # }
