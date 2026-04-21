import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from easy_st_aggrid import *

st.set_page_config(
    layout='wide'
)

df = pd.DataFrame({
    "item": ["A", "B", "C", "D", "E"],
    "type": ["Tech", "Tech", "Hogar", "Hogar", "Tech"],
    "price": [100, 200, 150, 300, 250],
    "quantity": [5, 3, 8, 2, 6],
    "date": ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01",],
    "date2": ["2026-01-01", "2026-02-01", "2200-01-01", None, None,],
    "booli": [1,0,1,0,True],
})

df['booli'] = df['booli'].astype(bool)
# df["date2"] = pd.to_datetime(df["date2"], errors='coerce').dt.date  

cols = [
    # col_base("type", rowGroup=True),
    col_base(alias='📁', children=[
        col_bool("booli",
            # alias="Boolean", 
            filter=True,
            # values={True:'👌', False: 'x'}
            headerTooltip='columna booleana',
        ),
        col_str_date('date2', 
            enableRowGroup=True, 
            # rowGroup=True,
        ),
    ]),

]

st.title("TABLE")

# st.write(df['date2'])
result = easy_table(
    df,
    # select_checkbox=True,
    columns_list=cols,
    # floatingFilter=True,
    theme='dark',
    select_checkbox=True,
    selection_multiple=True,
    # row_grouping=True,
    enterprise=True,
)


st.header('RESPONSE')
with st.expander('columns_state'):
    st.dataframe(result.columns_state)
    st.write( str( type(result.columns_state) ) )

with st.expander('data'):
    st.dataframe(result.data)
    st.write( str( type(result.data) ) )

with st.expander('selected_data'):
    st.dataframe(result.selected_data)
    st.write( str( type(result.selected_data) ) )