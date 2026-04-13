from typing import Optional
from dataclasses import dataclass

from easy_st_aggrid.defaults import col_base
from st_aggrid import JsCode


def _find_col_bars(cols):
    """Busca col_bar en toda la jerarquía de columnas."""
    for c in cols:
        if isinstance(c, col_bar):
            yield c
        if hasattr(c, 'children') and c.children:
            yield from _find_col_bars(c.children)

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