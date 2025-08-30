import datetime
import json
import sys

import active.active as active

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data
def df_to_csv(df):
    return df.to_csv().encode("utf-8")

def draw_dataframe_gui(data_store, config):
    
    ids = data_store.get_ids()
    
    if len(ids) == 0:
        st.write("PostgreSQL database contains no data tables.")
        
    else:
        id = st.selectbox("Collection", ids)
        
        #df = st.dataframe(data_store.load(id))
        data = data_store.load(id)
        df = pd.DataFrame(data, columns = data_store.get_column_names(id)) 

        draw_dataframe_plot(df, id, config)
        
def draw_files_gui(data_store, config):
    '''
    
    '''
    
    ids = data_store.get_ids()
    
    id = st.selectbox("Collection", ids)
    
    files = data_store.get_names(id)
    
    for f in files:
        if f.endswith(".png") or f.endswith(".jpg"):
            st.image(f)
            
        if f.endswith(".csv"):
            
            st.download_button(
                data=open(f, "r"),
                file_name=f,
                label="Download " + f,
                mime="text/csv"
            )
            
            st.dataframe(pd.read_csv(f))
            
        else:
            st.download_button(
                data=open(f, "r"),
                file_name=f,
                label="Download " + f,
                mime="text/csv"
            )
    

def draw_dataframe_plot(df, id, config):
    '''
    
    '''
    
    datetime_cols = df.select_dtypes(include=['datetime64'])
    
    
    
    x_column = None
    
    if len(datetime_cols) == 0:
        x_column = df.columns[0]
        
    else:
        
        x_column = st.selectbox("X Axis", datetime_cols.columns)
        
    # dtypes = df.dtypes
    #
    # for i in range(len(df.columns)):
    #
    #     if type(dtypes.iloc[i]) == np.dtypes.DateTime64DType:
    #         x_column = df.columns[i]
    #         break
    #
    # if not x_column:
    #     x_column = df.columns[0]
    
    # Add a plotly line graph
    fig = px.line(df, x=x_column, y=df.select_dtypes(include='number').columns,
              title=config["name"] + " " + id)
    
    st.plotly_chart(fig)
    
    csv_contents = df_to_csv(df)
    st.download_button(
        data=csv_contents,
        file_name=config["name"] + "_" + id + ".csv",
        label="Download CSV",
        mime="text/csv"
    )

def render(env_files):
    
    environments = []
    
    for env_file in env_files:
        environments.append(env_file)
        
    if len(environments) == 0:
        st.write("No Environments found.")
    
    else:    
        environment_file = st.selectbox("Environment", environments)
            
        with open(environment_file) as env:
            config = json.load(env)
            
    
            
            controllers = {}
            data_stores = {}
            emulators = {}
            multiplexers = {}
            
            
            data_store_names = []
            
            if "data stores" in config:
                for ds in config["data stores"]:
                    data_store_names.append(ds["name"])
                    active._create_data_store(ds, controllers, data_stores, emulators, multiplexers, config)
            
                    
            if len(data_store_names) == 0:
                st.write("No data stores defined in selected environment.")
                
            else:
                data_store_name = st.selectbox("Data Store", data_store_names)
                
                data_store_config = None
                for ds in config["data stores"]:
                    if ds["name"] == data_store_name:
                        data_store_config = ds
                        break
                
                data_store = data_stores[data_store_name]
                
                viz_type = data_store.get_visualization_type()
                
                if "DATAFRAME" == viz_type:
                    draw_dataframe_gui(data_store, data_store_config)
                    
                elif "FILES" == viz_type:
                    draw_files_gui(data_store, data_store_config)
                    
                elif "NONE" == viz_type:
                    st.write("Data store of type " + data_store_config["type"] + 
                             "cannot be visualized.")
                    
                else:
                    st.write("Data store requested unknown visualization type: " + viz_type)
                


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(sys.argv[1:])
    