'''
Toolkit to create 'columnDefs' in a more pythonist way

Columns
-------
col_base
col_text
col_date
col_checkbox
col_status ** Under Test

Style
-----
cell_style

Table
-----
easy_table
'''
import warnings
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


## FIELDS / UNDER TEST

@dataclass
class col_status_new(col_base):
    """
    Strict status column:
    - Requires explicit states
    - No defaults allowed
    - CSS generated from Python
    - Renderer minimal & efficient
    """

    states: List["col_status_new.state"] = field(default_factory=list)

    def __post_init__(self):

        if self.filter:
            self.filter = "agSetColumnFilter"

        if not self.states:
            raise ValueError(
                "col_status requires a non-empty 'states' list."
            )

        status_map_js = self.state.get_json(self.states)

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
                txt.textContent = entry.label;

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
                return entry ? entry.label : "";
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
        label: str
        color: str

        @classmethod
        def get_json(cls, states: List["col_status.state"]) -> str:
            ids = set()
            for s in states:
                if s.id is None:
                    raise ValueError("State id cannot be None.")
                if s.id in ids:
                    raise ValueError(f"Duplicate state id detected: {s.id}")
                if not s.label:
                    raise ValueError(f"State label cannot be empty (id={s.id}).")
                if not s.color:
                    raise ValueError(f"State color cannot be empty (id={s.id}).")
                ids.add(s.id)
            
            map = {
                s.id: {'label': s.label, 'color': s.color} 
                for s in states
            }
            return json.dumps(map)

@dataclass
class col_bool(col_base):
    """
    Boolean column with a nice pill renderer.
    """
    true_label: str = "Sí"
    false_label: str = "No"

    def __post_init__(self):
        warnings.warn(
            "col_bool() está deprecada y será eliminada en una futura versión. "
            "se recomienda cambiar por la clase col_status(). ",
            DeprecationWarning,
            stacklevel=2
        )
        print("Ejecutando función antigua")
        
        if self.filter:
            self.filter = "agSetColumnFilter"
        if self.width is None:
            self.width = 90
        if self.minWidth is None:
            self.minWidth = 80
        if self.maxWidth is None:
            self.maxWidth = 120
        self.centered = True

        true_label_js = json.dumps(self.true_label)
        false_label_js = json.dumps(self.false_label)

        _BOOL_RENDERER = JsCode(f"""
        class BoolPillRenderer {{
            init(params) {{
                const raw = params.value;
                const toBool = (v) => {{
                    if (v === null || v === undefined || v === '') return false;
                    if (typeof v === 'boolean') return v;
                    if (typeof v === 'number') return v === 1;
                    const s = String(v).trim().toLowerCase();
                    return (s === 'true' || s === '1' || s === 'yes' || s === 'y' || s === 'si' || s === 'sí');
                }};

                const val = toBool(raw);
                const color = val ? '#2ecc71' : '#e74c3c';
                const bg = color + '22';
                const label = val ? {true_label_js} : {false_label_js};
                const iconName = val ? 'check' : 'close';
                const uid = 'b_' + Math.random().toString(36).substr(2, 9);

                // --- Inyectar fuente Material Symbols una sola vez ---
                if (!document.getElementById('_mat_sym_link')) {{
                    const link = document.createElement('link');
                    link.id = '_mat_sym_link';
                    link.rel = 'stylesheet';
                    link.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
                    document.head.appendChild(link);
                }}

                this.eGui = document.createElement('div');
                this.eGui.style.cssText =
                    'display:inline-flex;align-items:center;gap:10px;' +
                    'padding:4px 10px;border-radius:999px;' +
                    'background:' + bg + ';border:1px solid ' + color + '55;' +
                    'color:' + color + ';font-weight:800;font-size:12px;' +
                    'line-height:1;white-space:nowrap;';

                const iconWrap = document.createElement('span');
                iconWrap.className = 'material-symbols-outlined';
                iconWrap.textContent = iconName;
                iconWrap.style.cssText =
                    'font-size:18px;color:' + color +
                    ';opacity:0;transform:scale(0.6);' +
                    'animation:' + uid + '_pop 240ms ease-out forwards;';

                const text = document.createElement('span');
                text.textContent = label;
                text.style.opacity = '0';
                text.style.transform = 'translateX(-4px)';
                text.style.animation = uid + '_slide 260ms 80ms ease-out forwards';

                this.eGui.appendChild(iconWrap);
                this.eGui.appendChild(text);

                const style = document.createElement('style');
                style.textContent =
                    '@keyframes ' + uid + '_pop {{to{{opacity:1;transform:scale(1)}}}}' +
                    '@keyframes ' + uid + '_slide {{to{{opacity:1;transform:translateX(0)}}}}';
                this.eGui.appendChild(style);
            }}
            getGui() {{ return this.eGui; }}
        }}
        """)

        value_getter = JsCode("""
        function(params){
            const v = params.data ? params.data[params.colDef.field] : params.value;
            if (v === null || v === undefined || v === '') return false;
            if (typeof v === 'boolean') return v;
            if (typeof v === 'number') return v === 1;
            const s = String(v).trim().toLowerCase();
            return (s === 'true' || s === '1' || s === 'yes' || s === 'y' || s === 'si' || s === 'sí');
        }
        """)

        self.kwargs.update({
            "cellRenderer": _BOOL_RENDERER,
            "valueGetter": value_getter,
        })

@dataclass
class col_bar(col_base):
    '''
    Diverging bar column.
    '''
    max_abs: Optional[float] = None

    def __post_init__(self):
        if self.filter:
            self.filter = 'agNumberColumnFilter'
        if self.max_abs is not None:
            self._build_renderer()

    def _build_renderer(self):
        max_val = self.max_abs if self.max_abs and self.max_abs > 0 else 1

        _BAR_RENDERER = JsCode(f"""
            class DivergingBarRenderer {{
                init(params) {{
                    this.eGui = document.createElement('div');
                    this.eGui.style.display = 'flex';
                    this.eGui.style.alignItems = 'center';
                    this.eGui.style.gap = '8px';
                    this.eGui.style.width = '100%';
                    this.eGui.style.overflow = 'hidden';

                    let val = parseFloat(params.value);
                    if (isNaN(val)) {{ this.eGui.innerHTML = params.value || ''; return; }}

                    const maxAbs = {max_val};
                    const pct = Math.min((Math.abs(val) / maxAbs) * 50, 50);
                    const color = val >= 0 ? '#e74c3c' : '#2ecc71';

                    const container = document.createElement('div');
                    container.style.flex = '1 1 auto';
                    container.style.minWidth = '0';
                    container.style.position = 'relative';
                    container.style.height = '12px';
                    container.style.background = '#e6e6e6';
                    container.style.borderRadius = '6px';
                    container.style.overflow = 'hidden';

                    const center = document.createElement('div');
                    center.style.position = 'absolute';
                    center.style.left = '50%';
                    center.style.top = '0';
                    center.style.width = '1px';
                    center.style.height = '100%';
                    center.style.background = '#999';
                    container.appendChild(center);

                    if (val !== 0) {{
                        const bar = document.createElement('div');
                        bar.style.position = 'absolute';
                        bar.style.top = '0';
                        bar.style.height = '100%';
                        bar.style.width = pct + '%';
                        bar.style.background = color;
                        if (val > 0) bar.style.left = '50%';
                        else bar.style.right = '50%';
                        container.appendChild(bar);
                    }}

                    const label = document.createElement('span');
                    label.style.flex = '0 0 auto';
                    label.style.fontSize = '13px';
                    label.style.fontWeight = '600';
                    label.style.minWidth = '45px';
                    label.style.textAlign = 'right';
                    label.style.whiteSpace = 'nowrap';
                    label.style.paddingRight = '40px';
                    label.textContent = val.toFixed(0);

                    this.eGui.appendChild(container);
                    this.eGui.appendChild(label);
                }}
                getGui() {{ return this.eGui; }}
            }}
            """)
        self.kwargs['cellRenderer'] = _BAR_RENDERER

@dataclass
class col_status(col_base):
    '''
    Status column with configurable color map
    '''
    status_map: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        warnings.warn(
            "col_status() está deprecada y será eliminada en una futura versión para no usar diccionarios. ",
            DeprecationWarning,
            stacklevel=2
        )
        print("Ejecutando función antigua")


        if self.filter:
            self.filter = 'agTextColumnFilter'

        status_map = self.status_map or {
            "OK": "#2ecc71",
            "En riesgo": "#f39c12",
            "Crítico": "#e74c3c",
            "Bloqueado": "#7f8c8d",
        }
        status_map_js = json.dumps(status_map)

        _STATUS_RENDERER = JsCode(f"""
                class StatusRenderer {{
                    init(params) {{
                        const colorMap = {status_map_js};
                        const val = params.value || "";
                        const rawColor = colorMap[val] || "#999999";
                        let color = rawColor;
                        if (/^#[0-9a-fA-F]{{3}}$/.test(color)) {{
                            color = '#' + color[1]+color[1] + color[2]+color[2] + color[3]+color[3];
                        }}
                        const uid = 'st_' + Math.random().toString(36).substr(2, 9);

                        this.eGui = document.createElement('span');
                        this.eGui.style.cssText =
                            'display:inline-flex;align-items:center;gap:14px;' +
                            'background:' + color + '22;color:' + color + ';' +
                            'padding:4px 10px;border-radius:12px;font-weight:600;font-size:12px;';

                        const txt = document.createElement('span');
                        txt.textContent = val;

                        const dotWrap = document.createElement('div');
                        dotWrap.style.cssText = 'position:relative;width:8px;height:8px;flex-shrink:0;';

                        const dot = document.createElement('div');
                        dot.style.cssText =
                            'width:8px;height:8px;border-radius:50%;background:' + color +
                            ';position:absolute;top:0;left:0;';
                        dotWrap.appendChild(dot);

                        const ring = document.createElement('div');
                        ring.style.cssText =
                            'position:absolute;top:-3px;left:-3px;width:14px;height:14px;' +
                            'border-radius:50%;border:1.5px solid ' + color + ';opacity:0;' +
                            'animation:' + uid + '_pulse 2s ease-out infinite;';
                        dotWrap.appendChild(ring);

                        this.eGui.appendChild(txt);
                        this.eGui.appendChild(dotWrap);

                        const style = document.createElement('style');
                        style.textContent =
                            '@keyframes ' + uid + '_pulse {{' +
                            '0%{{opacity:.6;transform:scale(.7)}}' +
                            '100%{{opacity:0;transform:scale(2)}}}}';
                        this.eGui.appendChild(style);
                    }}
                    getGui() {{ return this.eGui; }}
                }}
                """)

        self.kwargs.update({'cellRenderer': _STATUS_RENDERER})

@dataclass
class col_progress(col_base):
    '''
    Progress Column
    '''
    def __post_init__(self):
        if self.filter:
            self.filter = 'agNumberColumnFilter'

        _PROGRESS_RENDERER = JsCode("""
            class ProgressRingRenderer {
                init(params) {
                    let val = parseFloat(params.value);
                    if (isNaN(val)) { this.eGui = document.createElement('span'); this.eGui.textContent = params.value || ''; return; }
                    val = Math.max(0, Math.min(100, val));

                    const size = 40;
                    const stroke = 4;
                    const radius = (size - stroke) / 2;
                    const circ = 2 * Math.PI * radius;
                    const offset = circ * (1 - val / 100);

                    let color;
                    if (val >= 80) color = '#2ecc71';
                    else if (val >= 50) color = '#3498db';
                    else if (val >= 25) color = '#f39c12';
                    else color = '#e74c3c';

                    this.eGui = document.createElement('div');
                    this.eGui.style.display = 'flex';
                    this.eGui.style.alignItems = 'center';
                    this.eGui.style.justifyContent = 'center';

                    this.eGui.innerHTML = `
                        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                            <circle cx="${size/2}" cy="${size/2}" r="${radius}"
                                fill="none" stroke="#e9ecef" stroke-width="${stroke}"/>
                            <circle cx="${size/2}" cy="${size/2}" r="${radius}"
                                fill="none" stroke="${color}" stroke-width="${stroke}"
                                stroke-dasharray="${circ}" stroke-dashoffset="${circ}"
                                stroke-linecap="round"
                                transform="rotate(-90 ${size/2} ${size/2})">
                                <animate attributeName="stroke-dashoffset"
                                    from="${circ}" to="${offset}"
                                    dur="0.9s" fill="freeze"
                                    calcMode="spline"
                                    keySplines="0.4 0 0.2 1"/>
                            </circle>
                            <text x="50%" y="53%" dominant-baseline="middle" text-anchor="middle"
                                font-size="11" font-weight="800" fill="${color}"
                                font-family="Segoe UI, sans-serif"
                                style="opacity:0">
                                ${Math.round(val)}%
                                <animate attributeName="opacity" from="0" to="1"
                                    dur="0.3s" begin="0.55s" fill="freeze"/>
                            </text>
                        </svg>
                    `;
                }
                getGui() { return this.eGui; }
            }
        """)

        self.kwargs.update({'cellRenderer': _PROGRESS_RENDERER})

@dataclass
class col_icon(col_base):
    '''
    Columna de estado con icono Google Material, color y label configurables.

    El usuario debe usar directamente el nombre del icono de Google Material
    Icons en el campo "icon" del status_map.
    Catálogo completo: https://fonts.google.com/icons

    Parameters
    ----------
    status_map : Dict[str, Dict]
        Diccionario donde cada clave es un valor posible de la columna y
        cada valor es un dict con:
            - "color" : str (hex color, e.g. "#e74c3c")
            - "label" : str (descripción que aparece debajo del código)
            - "icon"  : str (nombre directo del Material Icon, e.g. "schedule", "inventory_2")

    icon_size : int
        Tamaño del icono en px. Default: 22

    filled : bool
        Si True, usa variante rellena (FILL=1). Default: False.
        Solo aplica si la fuente cargada soporta font-variation-settings.

    Ejemplo
    -------
    status_map={
        "OrdPrv": {"color": "#e6b800", "label": "Orden Provisional", "icon": "schedule"},
        "Stock":  {"color": "#27ae60", "label": "En Stock",          "icon": "inventory_2"},
    }
    '''
    status_map: Dict[str, Dict[str, str]] = field(default_factory=dict)
    icon_size: int = 22
    filled: bool = False

    def __post_init__(self):
        if self.filter:
            self.filter = 'agTextColumnFilter'

        # Fallback
        status_map = self.status_map or {
            "Nivel 0": {"color": "#00fff2", "label": "Padre del Proyecto",    "icon": "crown"},
            "OrdPrv":  {"color": "#e6b800", "label": "Orden Provisional",     "icon": "schedule"},
            "SolPed":  {"color": "#e67e22", "label": "Solicitud de Pedido",   "icon": "description"},
            "CPExt":      {"color": "#8B5E3C", "label": "Otro Centro Producción","icon": "factory"},
            "OrdFab":  {"color": "#8e44ad", "label": "Orden de Fabricación",  "icon": "settings"},
            "RepPed":  {"color": "#2e86de", "label": "Reparto de Pedido",     "icon": "call_split"},
            "Stock":   {"color": "#27ae60", "label": "Stock de Centro",       "icon": "inventory_2"},
            "StcPry":  {"color": "#27ae60", "label": "Stock de Proyecto",     "icon": "inventory_2"},
            "ResOrd":  {"color": "#2c3e50", "label": "Resolución de Orden",   "icon": "check_circle"},
        }

        # Build config map for JS
        config_js = {}
        for key, cfg in status_map.items():
            config_js[key] = {
                "color": cfg.get("color", "#95a5a6"),
                "label": cfg.get("label", key),
                "icon": cfg.get("icon", "circle"),
            }

        config_js_str = json.dumps(config_js)
        icon_size = self.icon_size
        filled_flag = self.filled

        _ICON_RENDERER = JsCode(f"""
        class IconStatusRenderer {{
            init(params) {{
                const configMap = {config_js_str};
                const iconSize = {icon_size};
                const filled = {'true' if filled_flag else 'false'};

                // --- Inyectar fuente Material Symbols una sola vez ---
                if (!document.getElementById('_mat_sym_link')) {{
                    const link = document.createElement('link');
                    link.id = '_mat_sym_link';
                    link.rel = 'stylesheet';
                    link.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
                    document.head.appendChild(link);
                }}

                const val = (params.value || "").trim();
                const uid = 'is_' + Math.random().toString(36).substr(2, 9);

                const cfg = configMap[val] || {{
                    color: "#95a5a6",
                    label: val,
                    icon: "circle"
                }};
                const color = cfg.color;
                const materialIcon = cfg.icon;

                this.eGui = document.createElement('div');
                this.eGui.style.cssText = 'display:flex;align-items:center;gap:8px;';

                // --- Icon circle ---
                const iconWrap = document.createElement('div');
                iconWrap.style.cssText =
                    'width:32px;height:32px;border-radius:50%;' +
                    'background:' + color + '15;' +
                    'display:flex;align-items:center;justify-content:center;flex-shrink:0;' +
                    'opacity:0;animation:' + uid + '_iconPop 0.4s 0.08s cubic-bezier(0.34,1.56,0.64,1) forwards;';

                const iconEl = document.createElement('span');
                iconEl.className = 'material-symbols-outlined';
                iconEl.textContent = materialIcon;
                iconEl.style.cssText =
                    'font-size:' + iconSize + 'px;color:' + color + ';' +
                    'user-select:none;line-height:1;' +
                    (filled ? 'font-variation-settings:"FILL" 1;' : '');
                iconWrap.appendChild(iconEl);

                // --- Text block ---
                const textBlock = document.createElement('div');
                textBlock.style.cssText =
                    'display:flex;flex-direction:column;gap:0px;min-width:0;' +
                    'opacity:0;animation:' + uid + '_textSlide 0.35s 0.18s ease-out forwards;';

                const codeLine = document.createElement('span');
                codeLine.style.cssText =
                    'font-size:12.5px;font-weight:800;color:' + color +
                    ';letter-spacing:0.3px;line-height:1.2;';
                codeLine.textContent = val;

                const descLine = document.createElement('span');
                descLine.style.cssText =
                    'font-size:10.5px;color:#888;font-weight:500;line-height:1.2;' +
                    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
                descLine.textContent = cfg.label;

                textBlock.appendChild(codeLine);
                textBlock.appendChild(descLine);

                this.eGui.appendChild(iconWrap);
                this.eGui.appendChild(textBlock);

                const style = document.createElement('style');
                style.textContent =
                    '@keyframes ' + uid + '_iconPop{{from{{opacity:0;transform:scale(0) rotate(-45deg)}}to{{opacity:1;transform:scale(1) rotate(0deg)}}}}' +
                    '@keyframes ' + uid + '_textSlide{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:translateX(0)}}}}';
                this.eGui.appendChild(style);
            }}
            getGui() {{ return this.eGui; }}
        }}
        """)

        self.kwargs.update({'cellRenderer': _ICON_RENDERER})


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
        # getRowStyle: str = None,
        select_checkbox: bool = True,
        fit_columns_on_grid_load: bool = False,
        height: int = None,
        row_height: int = 40,
        floatingFilter: bool = False,
        statusbar: bool = False,
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

    # DEFAULT CONFIG
    gb.configure_grid_options( # Aqui los defaults
        # statusBar=statusBar_enterprise,
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