from snowflake.snowpark.session import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import *
from snowflake.snowpark import Window

from io import StringIO
import streamlit as st
import pandas as pd
import json
import numpy as np

st.set_page_config(page_title='CSV Snowpark Uploader',  initial_sidebar_state="auto", menu_items=None)
ss = st.session_state
session = ''
#st.write(ss)
if not ss:
        ss.pressed_first_button = False

#@st.cache_data
with st.sidebar:
    
    SF_ACCOUNT = st.text_input('Snowflake Account ( ab12345.ca-central-1.aws ):')
    SF_USR = st.text_input('Snowflake USER ( TYANG ):')
    SF_PWD = st.text_input('Snowflake authenticator:', type='password')

      
    conn = {'ACCOUNT': SF_ACCOUNT,'USER': SF_USR,'authenticator': SF_PWD}
     
     
    if st.button('Connect') or ss.pressed_first_button:             
            session = Session.builder.configs(conn).create()
            ss.pressed_first_button = True
             
            if session != '':
                datawarehouse_list = session.sql("show warehouses;").collect()
                datawarehouse_list =  pd.DataFrame(datawarehouse_list)
                datawarehouse_list= datawarehouse_list["name"]

                datawarehouse_option = st.selectbox('Select Virtual datawarehouse', datawarehouse_list)

                database_list_df = session.sql("show databases;").collect()
                database_list_df =  pd.DataFrame(database_list_df)
                database_list_df = database_list_df["name"]
                
                database_option = st.selectbox('Select database', database_list_df)
                set_database = session.sql(f'''USE DATABASE {database_option}   ;''').collect()

                if set_database != '':
                    set_database = session.use_database(database_option)
                    schema_list_df = session.sql("show schemas;").collect()
                    schema_list_df =  pd.DataFrame(schema_list_df)
                    schema_list_df = schema_list_df["name"]

                    schema_option = st.selectbox('Select schema', schema_list_df)
                    set_schema = session.sql(f'''USE schema {schema_option}   ;''').collect()

                    if set_schema != '':
                        table_list_df = session.sql("show tables;").collect()
                        table_list_df =  pd.DataFrame(table_list_df)
                        if not table_list_df.empty:
                            table_list_df = table_list_df["name"]

                            table_option = st.selectbox('Select tables', table_list_df)
                            upload_table = st.text_input('Use table:',table_option)

                            conn2 = {
                                    'ACCOUNT': SF_ACCOUNT,
                                    'user': SF_USR,
                                    'authenticator': SF_PWD,
                                    'schema': schema_option,
                                    'database': database_option,
                                    'warehouse': datawarehouse_option,
                                }

with st.container():
    if session != '':    
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            if uploaded_file.type == 'text/csv':
                #bytes_data = uploaded_file.getvalue()

                # To convert to a string based IO:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

                # To read file as string:
                string_data = stringio.read()

                # Can be used wherever a "file-like" object is accepted:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df)  # Same as st.write(df)

                Mode = 'Append' 
                #st.radio("Select mode",('Overwrite','Append'))

                if st.button('Upload'):
                    session = Session.builder.configs(conn2).create()
                    df = session.create_dataframe(df)
                    try:
                            if Mode == 'Overwrite':
                                df.write.mode('Overwrite').save_as_table(upload_table)
                            else:
                                df.write.mode('append').save_as_table(upload_table)
                    except ValueError:
                        st.error('Upload failed')
                    else:
                        st.write('File uploaded')
