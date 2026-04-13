'''
Toolkit to create 'columnDefs' in a more pythonist way

Columns
-------
col_base
col_text
col_bool
col_str_date
col_status

Style
-----
cell_style

Table
-----
easy_table
'''
from ._version import __version__
from st_aggrid import JsCode

from easy_st_aggrid.defaults import \
    cell_style, \
    default_cell, \
    default_header, \
    col_base, \
    col_text, \
    col_bool, \
    col_str_date

from easy_st_aggrid.table import easy_table

## CUSTOM COLUMNS
from easy_st_aggrid.col_status import col_status