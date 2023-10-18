import pandas as pd
import mgrs
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import streamlit as st

# Set the app wide layout
st.set_page_config(layout="wide")

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    r = 6371.0 # Radius of earth in kilometers. Use 3956 for miles
    return r * c

def mgrs_to_latlon(data):
    m = mgrs.MGRS()
    try:
        lat, lon = m.toLatLon(data)
        return lat, lon
    except Exception as e:
        st.write(f"Error converting {data}: {e}")
        return None, None

def process_dataframe(data):
    data['Latitude'], data['Longitude'] = zip(*data['MGRS'].apply(mgrs_to_latlon))
    data.dropna(inplace=True)
    
    data['DTG'] = pd.to_datetime(data['DTG'], format='%Y%m%d %H:%M%z')
    data = data.sort_values(by=['AdID', 'DTG'])

    distances = [0]
    for i in range(1, len(data)):
        lat1, lon1 = data['Latitude'].iloc[i-1], data['Longitude'].iloc[i-1]
        lat2, lon2 = data['Latitude'].iloc[i], data['Longitude'].iloc[i]
        distances.append(haversine(lat1, lon1, lat2, lon2))
    data['Distance'] = distances

    data['TimeDifference'] = data['DTG'].diff().dt.total_seconds().fillna(0)
    data['Distance'] *= 0.621371 # Convert the distance from km to miles
    data['Speed (mph)'] = data['Distance'] / (data['TimeDifference'] / 3600)
    
    # For rows where AdID changes, set speed to NaN
    data.loc[data['AdID'] != data['AdID'].shift(), 'Speed (mph)'] = np.nan

    return data[['AdID', 'DTG', 'Latitude', 'Longitude', 'Speed (mph)']]

def highlight_cells(data):
   # Define the legend HTML
    legend_html = """
    <div>
    <span style='background-color: green; padding: 5px; color: white;'>Under 75: Green</span>
    <span style='background-color: yellow; padding: 5px;'>75-100: Yellow</span>
    <span style='background-color: red; padding: 5px; color: white;'>100-350: Red</span>
    <span style='background-color: blue; padding: 5px; color: white;'>350-550: Blue</span>
    <span style='background-color: grey; padding: 5px; color: white;'>550 and above: Grey</span>
    </div>
    """
    
    # Start the HTML table
    html = "<table>"
    
    # Header
    html += "<thead><tr>"
    for col in data.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead>"
    
    # Body
    html += "<tbody>"
    for _, row in data.iterrows():
        html += "<tr>"
        for col, val in row.items():
            # For the 'Speed (mph)' column, apply conditional formatting
            if col == 'Speed (mph)':
                if val < 75:
                    html += f"<td style='background-color: green;'>{val}</td>"
                elif 75 <= val < 100:
                    html += f"<td style='background-color: orange;'>{val}</td>"
                elif 100 <= val < 350:
                    html += f"<td style='background-color: red;'>{val}</td>"
                elif 350 <= val < 575:
                    html += f"<td style='background-color: blue;'>{val}</td>"
                else:
                    html += f"<td style='background-color: red;'>{val}</td>"
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"
    html += "</tbody>"
    
    # End the HTML table
    html += "</table>"
    
    return html

# Streamlit UI
st.markdown("<h1 style='text-align: center; color: white;'>Spartan Baraq</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        result = process_dataframe(data)
        
        # Define the legend HTML
        legend_html = """
        <div>
            <span style='background-color: green; padding: 5px; color: white;'>Under 75 MPH: Green</span>
            <span style='background-color: orange; padding: 5px;'>75-100 MPH: Orange</span>
            <span style='background-color: red; padding: 5px; color: white;'>100-350 MPH: Red</span>
            <span style='background-color: blue; padding: 5px; color: white;'>350-575 MPH: Blue</span>
            <span style='background-color: red; padding: 5px; color: white;'>576 MPH and above: Red</span>
        </div>
        """
        
        # Extract unique AdIDs
        unique_AdIDs = result['AdID'].unique()

        # Create a dropdown select box for AdIDs
        selected_AdID = st.selectbox('Choose an AdID:', unique_AdIDs)

        # Filter data based on the selected AdID
        filtered_data = result[result['AdID'] == selected_AdID]

        # Display the filtered data table for the selected AdID
        st.markdown(legend_html, unsafe_allow_html=True)
        st.markdown(highlight_cells(filtered_data), unsafe_allow_html=True)
        

    except Exception as e:
        st.write(f"An error occurred: {e}")