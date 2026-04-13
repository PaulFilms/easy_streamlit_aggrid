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
from easy_st_aggrid import *


# from icons import *

import pandas as pd

# if TYPE_CHECKING:
#     import pandas as pd


def build_hierarchy(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    df = df.reset_index(drop=True)
    stack = []
    paths = []

    for idx, row in df.iterrows():
        lvl = int(row[col_name]) + 1  # ← normalizar: 0→1, 1→2, 2→3...

        while len(stack) >= lvl:
            stack.pop()

        stack.append(str(idx))
        paths.append(list(stack))

    df["hierarchy"] = [json.dumps(p) for p in paths]
    return df





## FIELDS



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

        # if self.filter:
        #     self.filter = 'agTextColumnFilter'

 
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

                // ★ Adaptar al rowHeight
                const rh       = (params.node && params.node.rowHeight) || 35;
                const fontSize  = Math.max(9, Math.min(12, Math.floor(rh * 0.32)));
                const padV      = Math.max(1, Math.floor(rh * 0.06));
                const padH      = Math.max(4, Math.floor(rh * 0.2));
                const gapSize   = Math.max(4, Math.floor(rh * 0.18));
                const dotSize   = Math.max(4, Math.min(8, Math.floor(rh * 0.18)));
                const ringSize  = dotSize + 6;
                const ringOff   = Math.floor((ringSize - dotSize) / 2);

                this.eGui = document.createElement('span');
                this.eGui.style.cssText =
                    'display:inline-flex;align-items:center;' +
                    'gap:' + gapSize + 'px;' +
                    'background:' + color + '22;color:' + color + ';' +
                    'padding:' + padV + 'px ' + padH + 'px;' +
                    'border-radius:12px;font-weight:600;' +
                    'font-size:' + fontSize + 'px;' +
                    'box-sizing:border-box;max-height:' + (rh - 6) + 'px;';

                const txt = document.createElement('span');
                txt.textContent = val;

                const dotWrap = document.createElement('div');
                dotWrap.style.cssText =
                    'position:relative;width:' + dotSize + 'px;height:' + dotSize + 'px;flex-shrink:0;';

                const dot = document.createElement('div');
                dot.style.cssText =
                    'width:' + dotSize + 'px;height:' + dotSize + 'px;border-radius:50%;background:' + color +
                    ';position:absolute;top:0;left:0;';
                dotWrap.appendChild(dot);

                const ring = document.createElement('div');
                ring.style.cssText =
                    'position:absolute;top:-' + ringOff + 'px;left:-' + ringOff + 'px;' +
                    'width:' + ringSize + 'px;height:' + ringSize + 'px;' +
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

        self.kwargs['cellRenderer']= _STATUS_RENDERER

@dataclass
class col_progress(col_base):
    '''
    Progress Column - responsive to rowHeight
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

                    // ★ Adaptar al rowHeight
                    const rh = (params.node && params.node.rowHeight) || 35;
                    const size = Math.max(16, Math.min(40, rh - 6));
                    const stroke = Math.max(2, (size * 0.1) | 0);
                    const radius = (size - stroke) / 2;
                    const circ = 2 * Math.PI * radius;
                    const offset = circ * (1 - val / 100);
                    const txtSize = Math.max(7, (size * 0.275) | 0);

                    let color;
                    if (val >= 80) color = '#2ecc71';
                    else if (val >= 50) color = '#3498db';
                    else if (val >= 25) color = '#f39c12';
                    else color = '#e74c3c';

                    this.eGui = document.createElement('div');
                    this.eGui.style.display = 'flex';
                    this.eGui.style.alignItems = 'center';
                    this.eGui.style.justifyContent = 'center';
                    this.eGui.style.height = '100%';

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
                                font-size="${txtSize}" font-weight="800" fill="${color}"
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
        # if self.filter:
        #     self.filter = 'agTextColumnFilter'

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
                    const filled = {'true' if filled_flag else 'false'};

                    if (!document.getElementById('_mat_sym_link')) {{
                        const link = document.createElement('link');
                        link.id = '_mat_sym_link';
                        link.rel = 'stylesheet';
                        link.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
                        document.head.appendChild(link);
                    }}

                    const val = (params.value || "").trim();
                    const uid = 'is_' + Math.random().toString(36).substr(2, 9);
                    const cfg = configMap[val] || {{ color: "#95a5a6", label: val, icon: "circle" }};
                    const color = cfg.color;
                    const materialIcon = cfg.icon;

                    // ★ Adaptar al rowHeight
                    const rh = (params.node && params.node.rowHeight) || 35;
                    const wrapSize = Math.max(18, Math.floor(rh * 0.72));
                    const dynIconSize = Math.max(12, wrapSize - 10);
                    const codeFontSize = Math.max(9, Math.min(12.5, rh * 0.34));
                    const descFontSize = Math.max(8, Math.min(10.5, rh * 0.28));
                    const gapSize = Math.max(2, Math.floor(rh * 0.08));

                    this.eGui = document.createElement('div');
                    this.eGui.style.cssText = 'display:flex;align-items:center;gap:'+gapSize+'px;height:100%;';

                    const iconWrap = document.createElement('div');
                    iconWrap.style.cssText = 'width:'+wrapSize+'px;height:'+wrapSize+'px;border-radius:50%;'
                        + 'background:' + color + '15;'
                        + 'display:flex;align-items:center;justify-content:center;flex-shrink:0;'
                        + 'opacity:0;animation:' + uid + '_iconPop 0.4s 0.08s cubic-bezier(0.34,1.56,0.64,1) forwards;';

                    const iconEl = document.createElement('span');
                    iconEl.className = 'material-symbols-outlined';
                    iconEl.textContent = materialIcon;
                    iconEl.style.cssText = 'font-size:' + dynIconSize + 'px;color:' + color + ';'
                        + 'user-select:none;line-height:1;'
                        + (filled ? 'font-variation-settings:"FILL" 1;' : '');
                    iconWrap.appendChild(iconEl);

                    const textBlock = document.createElement('div');
                    textBlock.style.cssText = 'display:flex;flex-direction:column;gap:0px;min-width:0;'
                        + 'opacity:0;animation:' + uid + '_textSlide 0.35s 0.18s ease-out forwards;';

                    const codeLine = document.createElement('span');
                    codeLine.style.cssText = 'font-size:'+codeFontSize+'px;font-weight:800;color:' + color + ';letter-spacing:0.3px;line-height:1.2;';
                    codeLine.textContent = val;

                    const descLine = document.createElement('span');
                    descLine.style.cssText = 'font-size:'+descFontSize+'px;color:#888;font-weight:500;line-height:1.2;'
                        + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
                    descLine.textContent = cfg.label;

                    textBlock.appendChild(codeLine);
                    textBlock.appendChild(descLine);
                    this.eGui.appendChild(iconWrap);
                    this.eGui.appendChild(textBlock);

                    const style = document.createElement('style');
                    style.textContent = '@keyframes ' + uid + '_iconPop{{from{{opacity:0;transform:scale(0) rotate(-45deg)}}to{{opacity:1;transform:scale(1) rotate(0deg)}}}}'
                        + '@keyframes ' + uid + '_textSlide{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:translateX(0)}}}}';
                    this.eGui.appendChild(style);
                }}
                getGui() {{ return this.eGui; }}
            }}
            """)

        self.kwargs.update({'cellRenderer': _ICON_RENDERER})



## TABLE





