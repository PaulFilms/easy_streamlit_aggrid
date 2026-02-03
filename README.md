# easy_streamlit_aggrid
Toolkit for creating 'columnDefs' in a more pythonistic way for the 'streamlit-aggrid' component

![Last commit](https://img.shields.io/github/last-commit/PaulFilms/easy_streamlit_aggrid?label=Last_Commit)


## Source Links:

@PablocFonseca / streamlit-aggrid

[![PyPI][pypi_badge]][pypi_link] [![GitHub][github_badge]][github_link] 

AG Grid JavaScript Data Grid library 

<a href="https://www.ag-grid.com/">
<img src="https://cdn.cookielaw.org/logos/df8b363f-f4d9-4e0c-934e-b286bcd83e8c/67b88210-d43e-4471-8e61-2cd23a738cac/fb1b8970-8f6a-407e-b737-477cb14c94f0/ag-grid-logo.png" width=150 alt="image" url="www.hispasonic.com">
</a>


<br>

## Installation Method

   ```plaintext
   pip install git+https://github.com/PaulFilms/easy_streamlit_aggrid.git@main
   ```


<br>

## Examples

```Python

from easy_st_aggrid import col_base, col_text, col_date, col_checkbox, easy_table

df = pd.DataFrame(your_data)

columns_config = [
   col_checkbox(),
   col_text(id='id', alias='ID', filter=True, pinned=True,),
   col_base(id='info', alias='FECHAS',
      children=[
         col_date(id='fecha_ini', alias='FECHA INI', filter=True, width=130, minWidth=130, maxWidth=130, columnGroupShow='open',),
         col_date(id='fecha_fin', alias='FECHA FIN', filter=True, width=130, minWidth=130, maxWidth=130, pinned=True,),
      ],
   ),
]

selection = easy_table(
   dataframe=df, 
   columns_list=columns_config
)

if selection is not None and len(selection) > 0:
   print(selection)

``` 

### Styles

```Python

from easy_st_aggrid import col_base, col_text, col_date, col_checkbox, easy_table, JsCode

cell_style_dias = JsCode("""
   function(params) {
         if (params.value >= 0) {
            return { fontWeight: 'bold', color: 'green', "fontSize": "18px", "display": "flex", "alignItems": "center",};
         } else {
            return { fontWeight: 'bold', color: 'red', "fontSize": "18px", "display": "flex", "alignItems": "center", };
         }
   }
""")

columns_config = [
   col_text(id='dias', alias='DÍAS', 
         cellStyle=cell_style_dias,
   ),
]

```

<br>

## ⚠️ Warnings

- If the aggrid table is in another Streamlit layout such as St.Tab, the aggrid table does not render
- At the moment, only the following types of columns are implemented: col_text, col_date, col_checkbox



[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/PablocFonseca/streamlit-aggrid
[pypi_badge]: https://badgen.net/pypi/v/streamlit-aggrid?icon=pypi&color=black&label?
[pypi_link]: https://www.pypi.org/project/streamlit-aggrid/
