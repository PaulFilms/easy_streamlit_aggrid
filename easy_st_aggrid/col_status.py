import json
from typing import List
from dataclasses import dataclass, field

from st_aggrid import JsCode
from easy_st_aggrid import col_base

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