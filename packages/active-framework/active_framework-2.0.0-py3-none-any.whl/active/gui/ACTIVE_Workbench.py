import pathlib
import sys

import plotly.express as px
import streamlit as st

from streamlit.web import cli
from sys import argv
        
@st.cache_data
def df_to_csv(df):
    return df.to_csv().encode("utf-8")
    
def render():
    '''
    Display a graph for a data source's full data.
    '''
    
    st.markdown(
    """
    # ACTIVE Workbench
    ACTIVE (the Automated Control Testbed for Integration, Verification, and Emulation) is a framework for operation management and algorithm testing software designed for facility control. The ACTIVE Workbench provides a web-based GUI interface for interacting with an ACTIVE instance, allowing you to control Environments and view results from current Environments.
    ## Environment Manager
    Monitor and control running Environments, or start and stop Environments
    ## Data Store Visualization 
    Visualize the contents of Data Stores
    """
    )
    
def run(env_file):
    
    this_file = str(pathlib.Path(__file__).resolve())
    cli.main_run([this_file, env_file])
    
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="ACTIVE Workbench")
    print(sys.argv[1])
    render()
    