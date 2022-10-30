from random import sample
from select import select
import streamlit as st
import pandas as pd
import numpy as np
import folium
from datetime import time
from folium import plugins
from folium.plugins import Draw
from streamlit_folium import st_folium
from PIL import Image
import geocoder


rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'#0e1117',
          'axes.edgecolor': '#0e1117',
          'axes.labelcolor': 'white',
          'figure.facecolor': '#0e1117',
          'patch.edgecolor': '#0e1117',
          'text.color': 'white',
          'xtick.color': 'white',
          'ytick.color': 'white',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 8,
          'ytick.labelsize': 12}

slot2num = {'Midnight':0,
                'Morning':1,
                'Afternoon':2,
                'Night':3}


def make_cluster_map(df, center, zoom, map_style):
    '''
    A function to creat a cluster map by using folium
    '''
    chicago_cluster_map = folium.Map(location=center, zoom_start=zoom, tiles= map_style)
    marker_cluster = plugins.MarkerCluster().add_to(chicago_cluster_map)
    for name, row in df.iterrows():
        popup_text = """
                    District: {}<br>
                    Date: {}<br>
                    Description : {}<br>
                    Location Description : {}<br>
                    Arrest : {}<br>"""
        popup_text = popup_text.format(row['District'],
                                row['Date'],
                                row['Primary Type'],
                                row['Location Description'],
                                row['Arrest']
                                )
        popup = folium.Popup(popup_text,min_width = 300, max_width=500 )
        folium.Marker(location=[row["Latitude"], row["Longitude"]],popup= popup, fill = True).add_to(marker_cluster)
    folium.GeoJson(
    'geojson/chicago.json', 
    name='geojson',
    style_function = lambda feature: {
        'color':'red',
        'fillColor': 'red'
        }
    ).add_to(chicago_cluster_map)

    return chicago_cluster_map

def make_heat_map(df, center, zoom, map_style):
    '''
    A function to creat a heat map by using folium
    '''
    chicago_heat_map = folium.Map(location=center, zoom_start=zoom ,tiles= map_style)
    points=[]
    l=[]
    lati =df['Latitude'].to_list()
    long =df['Longitude'].to_list()
    for a in range(len(lati)):
        l.append([lati[a],long[a]])
        points.append(l[a])
        
    folium.GeoJson(
    'geojson/chicago.json', 
    name='geojson',
    style_function = lambda feature: {
        'color':'red',
        'fillColor': 'red'
        }
    ).add_to(chicago_heat_map)    

    plugins.HeatMap(points).add_to(chicago_heat_map)
    return chicago_heat_map

def geo_coder(location):
    return geocoder.arcgis(location).latlng

df = pd.read_csv('data/Chicago_crimes.csv').sample(10000)
df.drop(columns=['Unnamed: 0'], inplace=True)
df.Date = pd.to_datetime(df.Date)
df.index = pd.DatetimeIndex(df.Date)

df['Month_n'] = pd.DatetimeIndex(df['Date']).month_name()
df['Day'] = pd.DatetimeIndex(df['Date']).day
df['Day_n'] = pd.DatetimeIndex(df['Date']).day_name()
df['Time']=df['Date'].dt.time

sample = df.sample(5000)
lat = df['Latitude'].mean()
log = df['Longitude'].mean()
center = [lat, log]
zoom = 10.5

def app(df=sample):
    st.title('Shadows in the Sun - The guilty secret in a busy city')
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
    # with row0_2:
    #     st.text('')
    #     st.subheader('- The guilty secret in a busy city')

    # Image
    image = Image.open('skyline.jpg')
    st.image(image, caption='Hell is empty. The devil is on Chicago.')

    year = df['Year'].value_counts().index.to_list()
    month = df['Month_n'].value_counts().index.to_list()
    week_day = df['Day_n'].value_counts().index.to_list()
    crime_type = df['Primary Type'].value_counts().index.to_list()
    district = df['District'].value_counts().index.to_list()
    location = df['Location Description'].value_counts().index.to_list()

    # Selectors
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.header("Time Selector")

    with col1_2:
        st.header("Category Selector")
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        slot_filter_year = st.multiselect(
            'Choosing the years',
            year,
            [2013,2014,2015,2016])

    with col2_2:
        slot_filter_type = st.multiselect(
            'Choosing the crime types',
            crime_type,
            ['THEFT','NARCOTICS'])

    col3_1, col3_2 = st.columns(2)
    with col3_1:
        slot_filter_month = st.multiselect(
            'Choosing the months',
            month,
            ['April','May','June','July'])
    with col3_2:
        slot_filter_district = st.multiselect(
            'Choosing the districts',
            district,
            [2.0, 3.0, 4.0, 5.0, 6.0]) 
            
    col4_1, col4_2 = st.columns(2)
    with col4_1:
        slot_filter_week_day = st.multiselect(
            'Choosing the week of days',
            week_day,
            ['Saturday','Sunday'])
    with col4_2:
        slot_filter_location = st.multiselect(
            'Choosing the location',
            location,
            ['STREET','APARTMENT','RESIDENCE'])

    # Select the Data
    if slot_filter_year:
        df = df[df.Year.isin(slot_filter_year)]

    if slot_filter_month:
        df = df[df.Month_n.isin(slot_filter_month)]

    if slot_filter_week_day:
        df = df[df.Day_n.isin(slot_filter_week_day)]

    if slot_filter_type:
        df = df[df['Primary Type'].isin(slot_filter_type)]

    if slot_filter_district:
        df = df[df.District.isin(slot_filter_district)]

    if slot_filter_location:
        df = df[df['Location Description'].isin(slot_filter_location)]

    # Summary Digital Panel
    st.header('Crime Digital Panel')
    col1, col2, col3 = st.columns(3)
    col1.metric("Case Number", f"{len(df)}")
    col2.metric("Under Arrest", f"{len(df[df['Arrest'] == True])}")
    if len(df) != 0:
        col3.metric("Arrest Rate", f"{len(df[df['Arrest'] == True])/len(df):.1%}")
    else:
        col3.metric("Arrest Rate", "0")        

    # Map
    st.header('Crime Map')
    col5_1, col5_2 = st.columns(2)
    with col5_1:
        option = st.selectbox(
        'Which map you want to see?',
        ('Heat Map', 'Cluster Map'))
    
    with col5_2:
        option_s = st.selectbox(
        'Which map style you want?',
        ('Black and White','Normal')
        )

    location_check = st.text_input('Movie title', '')

    if option_s == 'Normal':
        map_style = 'OpenStreetMap'
    else:
        map_style = 'Stamen Toner'
    
    new_center = geo_coder(location_check)

    if new_center:
        new_zoom = 15
        if option == 'Heat Map':
            heat_map = make_heat_map(df, new_center, new_zoom, map_style)
            folium.Marker(location=new_center,icon=folium.Icon(color='red'),popup=folium.Popup(f'{location_check}',min_width = 300, max_width=500 )).add_to(heat_map)
            Draw(export=True).add_to(heat_map)
            st.data = st_folium(heat_map,width=1500)
        elif option == 'Cluster Map':
            cluster_map = make_cluster_map(df, new_center, new_zoom, map_style)
            folium.Marker(location=new_center,icon=folium.Icon(color='red'),popup=folium.Popup(f'{location_check}',min_width = 300, max_width=500 )).add_to(cluster_map)
            Draw(export=True).add_to(cluster_map)
            st.data = st_folium(cluster_map,width=1500)
    else:
        if option == 'Heat Map':
            heat_map = make_heat_map(df, center, zoom, map_style)
            Draw(export=True).add_to(heat_map)
            st.data = st_folium(heat_map,width=1500)
        elif option == 'Cluster Map':
            cluster_map = make_cluster_map(df, center, zoom, map_style)
            Draw(export=True).add_to(cluster_map)
            st.data = st_folium(cluster_map,width=1500)

