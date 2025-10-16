'''
Toolkit to create 'columnDefs' in a more pythonist way

Columns
-------
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
__all__ = [
    "JsCode",
    "cell_style",
    "col_base",
    "col_text",
    "col_date",
    "col_checkbox",
    "easy_table",
]

from dataclasses import dataclass, asdict, field
from typing import Optional, Union, List, Tuple, Dict, Any
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

from st_aggrid import AgGrid, JsCode, GridOptionsBuilder

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
        cell_dict['alignItems'] = "center" # "center" | "top" | "bottom"
        return cell_dict

default_cell = cell_style(
    fontSize=15,
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
    filter: Union[bool, str, None] = None
    width: Optional[int] = None
    minWidth: Optional[int] = None
    maxWidth: Optional[int] = None
    pinned: bool = False
    headerStyle: Optional[Dict[str, Any]] = None
    cellStyle: Optional[Dict[str, Any]] = None

    columnGroupShow: Union[bool, str, None] = None
    children: Optional[List[col_base]] = None
    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)
    

    def data(self) -> Dict[str, Any]:
        '''
        Returns a dictionary key, value from defined objects
        '''
        col_options = dict()

        col_options['field'] = self.id
        if self.alias != None:
            col_options["headerName"] = self.alias
        
        if isinstance(self.filter, str):
            col_options['filter'] = self.filter

        if self.width != None:
            col_options['width'] = self.width
        if self.minWidth != None:
            col_options['minWidth'] = self.minWidth
        if self.maxWidth != None:
            col_options['maxWidth'] = self.maxWidth
        if self.pinned:
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
        if self.filter:
            ## Se opta por agTextColumnFilter en vez de agDateColumnFilter por simplicidad
            self.filter = 'agTextColumnFilter' # "agDateColumnFilter", "filterParams": {"customFormatString": "yyyy-MM-dd", "browserDatePicker": True, "comparator": comparator}, 
        
        value_formatter_js = JsCode("""
            function(params) {
                if (params.value) {
                    const date = new Date(params.value);
                    const year = date.getFullYear();
                    const month = ('0' + (date.getMonth() + 1)).slice(-2);
                    const day = ('0' + date.getDate()).slice(-2);
                    return year + '-' + month + '-' + day;
                } else {
                    return '';
                }
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
    

## TABLE

def _columns_config(cls, columnas: List[col_base]) -> List[Dict]:
    '''
    Returns a list of dicts to be used in AgGrid columnDefs
    '''
    # Recibe una lista de objetos col_base y devuelve lista de dicts
    return [col.data() for col in columnas]

def easy_table(
        dataframe: 'pd.DataFrame', 
        columns_list: List[col_base], 
        cell_style: cell_style = default_cell, 
        fit_columns_on_grid_load: bool = True
    ) -> Any | str | pd.DataFrame | None:
    '''
    Render a dataframe with AgGrid and custom options
    '''

    ## DATAFRAME
    df = dataframe.copy()

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_side_bar(filters_panel=True)
    gb.configure_default_column(floatingFilter=True)
    gb.configure_selection(selection_mode="single", use_checkbox=True)

    grid_options = gb.build()

    grid_options['defaultColDef']["cellStyle"] = cell_style.to_dict()
    # grid_options['getRowStyle'] = row_style_js  # gb.configure_grid_options(getRowStyle=row_style_js)
    grid_options['columnDefs'] = _columns_config(columns_list) #  or col.children
    grid_options['suppressMovableColumns'] = True # Bloquear reordenar columnas
    grid_options['rowHeight'] = 50 # Definir altura fija de filas
    grid_options['columnDefs'][0]['checkboxSelection'] = True
    # grid_options['columnDefs'][0]['headerCheckboxSelection'] = True
    # grid_options['defaultColDef']['wrapText'] = True
    # grid_options['defaultColDef']['autoHeight'] = True

    ## TABLE
    response = AgGrid(
        df,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        height=None,  # opcional, ignora alto fijo
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        domLayout="autoHeight",
        theme='streamlit'
    )

    return response.selected_data