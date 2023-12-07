# impossible-journey tool
The impossible journey tool uses several libraries to create a web application that analyzes and visualizes the speed of ad-tech hits based on their MGRS coordinates. The tool converts MGRS coordinates to latitude and longitude, calculates the distance and speed between consecutive points, and highlight the speed values based on a stoplight +1 chart. The tool is visualized with streamlit to create a user interface that allows the user to upload a CSV file with columns AdID, DTG, and MGRS, and displays the processed data frame and the legend in an HTML table. 

#using the app

To run the app use streamlit run app.py

Insert your data and hit the run button
