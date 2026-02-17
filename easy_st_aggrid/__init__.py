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
from ._version import __version__
from .icons import Icons
from easy_st_aggrid.columns_config import \
    col_base, \
    col_text, \
    col_date, \
    col_checkbox, \
    col_status, \
    cell_style, \
    JsCode, \
    easy_table

## BUG: circular import when importing all the functions in columns_config.py
# import importlib

# def __getattr__(name):
#     if name in __all__:
#         mod = importlib.import_module(".columns_config", __name__)
#         return getattr(mod, name)
#     raise AttributeError(f"module {__name__} has no attribute {name}")
