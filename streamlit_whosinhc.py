import streamlit as st
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

"""
# Hardin County Jail
Here's our first attempt at using data to create a table:
"""
def main():
    df1 = load_data()
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration"])
    
    if page == "Homepage":
        st.header("This is your data explorer.")
        st.write("Please select a page on the left.")
        st.write(df1)
        
    elif page == "Exploration":
        st.title("Data Exploration")
        #think of something cool here?
     
def scrape():
    url = 'http://209.152.119.10/vine/currentinmates/currentinmates.html'
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all('tr')
    prisoner_rows = rows[1:]
    ar = np.array(prisoner_rows)
    prisoner_chunks = np.split(ar, len(prisoner_rows) / 6)

    def chunkdict(chunk):
        output = {}
        output["pic"] = chunk[0].find_all("img")[0]["src"]
        output["name"] = chunk[0].find_all("td")[-1].text
        output["age"] = chunk[1].find_all("td")[-1].text
        output["gender"] = chunk[2].find_all("td")[-1].text
        output["detained"] = chunk[3].find_all("td")[-1].text
        output["released"] = chunk[4].find_all("td")[-1].text
        output["charges"] = chunk[5].find_all("td")[-1].text
        return output
    prisoner_dicts = [chunkdict(x) for x in prisoner_chunks]
    df = pd.DataFrame(prisoner_dicts)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df = df[['name', 'gender', 'age', 'detained', 'charges', 'released', 'pic']]
    df_filtered = df[df['charges'].str.contains('ICE ', na = False)]
    df_filtered.insert(loc=0, column='Row Number', value=np.arange(len(df_filtered)))

    return(df_filtered)

    scrape()

df = pd.DataFrame(scrape())
df
    
@st.cache
def load_data():
    return df

st.subheader("How many people are currently detained?")
#Get a bool series representing which rows satisfy the condition of True for no
# date in released column
how_many = df.apply(lambda x: True if x['released'] == "-" else False, axis =1)
# Count number of True in series
numOfRows = len(how_many[how_many == True].index)
st.write("Number of people currently detained: ", numOfRows)

released = st.sidebar.multiselect('Create a table belowing showing only detainees with selected release dates:', df['released'].unique())

st.subheader("Use the search bar on the left to show detaines with a selected release date")
new_df = df[(df['released'].isin(released))]
st.write(new_df)

if __name__ =="__main__":
    main()
