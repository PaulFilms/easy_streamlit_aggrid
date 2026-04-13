import json
from typing import List, Union
from dataclasses import dataclass, field

from st_aggrid import JsCode
from easy_st_aggrid.defaults import col_base


@dataclass
class col_icon(col_base):
    """
    Status-like icon column based on explicit states.

    If a value is not configured (or states is empty), a gray fallback with
    a question-mark icon is rendered.
    """

    states: List["col_icon.state"] = field(default_factory=list)
    icon_size: int = 22
    filled: bool = False

    def __post_init__(self):
        states_map_js = self.state.get_json(self.states)
        fallback_color = "#95a5a6"
        fallback_icon = "question_mark"
        filled_flag = self.filled
        base_icon_size = self.icon_size if self.icon_size and self.icon_size > 0 else 22

        _ICON_RENDERER = JsCode(
            f"""
            class IconStatusRenderer {{
                init(params) {{
                    const map = {states_map_js};
                    const fallbackColor = '{fallback_color}';
                    const fallbackIcon = '{fallback_icon}';
                    const baseIconSize = {base_icon_size};
                    const filled = {'true' if filled_flag else 'false'};

                    if (!document.getElementById('_mat_sym_link')) {{
                        const link = document.createElement('link');
                        link.id = '_mat_sym_link';
                        link.rel = 'stylesheet';
                        link.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
                        document.head.appendChild(link);
                    }}

                    const val = String(params.value ?? "").trim();
                    const uid = 'is_' + Math.random().toString(36).substr(2, 9);
                    const cfg = map[val] || {{ color: fallbackColor, label: val, icon: fallbackIcon }};
                    const color = cfg.color;
                    const materialIcon = cfg.icon;

                    const rh = (params.node && params.node.rowHeight) || 35;
                    const wrapSize = Math.max(18, Math.floor(rh * 0.72));
                    const dynIconSize = Math.max(12, Math.min(baseIconSize, wrapSize - 6));
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
            """
        )

        self.kwargs.update({"cellRenderer": _ICON_RENDERER})

    @dataclass
    class state:
        id: Union[str, int]
        label: str
        color: str
        icon: str

        @classmethod
        def get_json(cls, states: List["col_icon.state"]) -> str:
            ids = set()
            parsed = {}

            for s in states:
                if s.id is None:
                    raise ValueError("Icon state id cannot be None.")

                key = str(s.id)
                if key in ids:
                    raise ValueError(f"Duplicate icon state id detected: {s.id}")
                if not s.label:
                    raise ValueError(f"Icon state label cannot be empty (id={s.id}).")
                if not s.color:
                    raise ValueError(f"Icon state color cannot be empty (id={s.id}).")
                if not s.icon:
                    raise ValueError(f"Icon state icon cannot be empty (id={s.id}).")

                ids.add(key)
                parsed[key] = {
                    "label": s.label,
                    "color": s.color,
                    "icon": s.icon,
                }

            return json.dumps(parsed)
