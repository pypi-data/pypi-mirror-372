import streamlit as st
from sqlalchemy import text, create_engine
from os import environ
from ucimlrepo import fetch_ucirepo

from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Life expentancy progression of countries per continents'),
    dcc.Graph(id="graph"),
    dcc.Checklist(
        id="checklist",
        options=["Asia", "Europe", "Africa","Americas","Oceania"],
        value=["Americas", "Oceania"],
        inline=True
    ),
])


@app.callback(
    Output("graph", "figure"), 
    Input("checklist", "value"))
def update_line_chart(continents):
    df = px.data.gapminder() # replace with your own data source
    mask = df.continent.isin(continents)
    fig = px.line(df[mask], 
        x="year", y="lifeExp", color='country')
    return fig


app.run_server(debug=True)


#DB_URI = "postgresql:8888"
#conn_st = st.connection(name="postgres", type='sql', url = DB_URI)
#iris_data = conn_st.query("SELECT * FROM iris")

st.title("Streamlit with Postgres Demo")

# Display Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Average Sepal Length (cm)", round(iris_data["sepal length"].mean(), 2))
with col2:
    st.metric("Average Sepal Width (cm)", round(iris_data["sepal width"].mean(), 2))
with col3:
    st.metric("Average Petal Length (cm)", round(iris_data["petal length"].mean(), 2))
with col4:
    st.metric("Average Petal Width (cm)", round(iris_data["petal width"].mean(), 2))

# Displays Scatterplot
st.header("Scatter Plot")

c1, c2 = st.columns(2)

with c1: 
    x = st.selectbox("Select X-Variable", options=iris_data.select_dtypes("number").columns, index=0)
with c2:
    y = st.selectbox("Select Y-Variable", options=iris_data.select_dtypes("number").columns, index=1)

scatter_chart = st.scatter_chart(iris_data, x=x, y=y, size=40, color='class')

# Displays Dataframe
st.dataframe(iris_data, use_container_width=True)

# Creates sidebar to add data
with st.sidebar:    
    reset = st.button("Reset Data")
    st.header("Add Iris Data")
    st.subheader("After submitting, a query is executed that inserts a new datapoint to the 'iris' table in our database.")
    with st.form(key='new_data'):
        sepal_length = st.text_input(label="Sepal Length (cm)", key=1)
        sepal_width = st.text_input(label="Sepal Width (cm)", key=2)
        petal_length = st.text_input(label="Petal Length (cm)", key=3)
        petal_width = st.text_input(label="Petal Width (cm)", key=4)
        iris_class = st.selectbox(label="Iris Class (cm)", key=5, options=iris_data["class"].unique())
        submit = st.form_submit_button('Add')
    st.subheader("After filling in the data fields and pressing 'Add', you should see the metrics, scatterplot, and dataframe update to represent the new point.")

# Replaces dataset in database with original 
if reset:
    upload_data(DB_URI)
    st.cache_data.clear()
    st.rerun()

# Inserts data into table
if submit:
    with conn_st.session as s:
        new_data = (sepal_length, sepal_width, petal_length, petal_width, iris_class)
        q = """
                INSERT INTO iris ("sepal length", "sepal width", "petal length", "petal width", "class")
                VALUES (:sepal_length, :sepal_width, :petal_length, :petal_width, :iris_class)
            """
        s.execute(text(q), {
            'sepal_length': sepal_length,
            'sepal_width': sepal_width,
            'petal_length': petal_length,
            'petal_width': petal_width,
            'iris_class': iris_class
        })
        s.commit()
    # Clears the cached data so that Streamlit fetches new data when updated. 
    st.cache_data.clear()
    st.rerun()