# yt_data_acquisition
#Purpose:

The application allows users to input a YouTube channel ID or URL and retrieve various data related to the channel, such as subscriber count, video count, and details of the latest videos.

#THINGS TO KNOW ABOUT CODE:

  #Required Installations:
  
    The code requires certain Python libraries (streamlit, pandas, google-api-python-client) to be installed via pip.
    
    Additionally, a valid Google API key with access to the YouTube Data API v3 is necessary for authentication.
    
  #Imports:
    The code begins with importing necessary libraries:
    
      -re: for working with regular expressions.
      
      -sqlite3: for interacting with SQLite databases.
      
      -googleapiclient.discovery: for accessing the YouTube Data API.
      
      -streamlit as st: for building interactive web applications.
      
      -pandas as pd: for data manipulation and analysis.
      
  #API Key:
  
    API_KEY: Your Google API key obtained from the Google Developer Console. This key is used to authenticate requests to the YouTube Data API.
    
  #Database Setup:
  
      -The create_tables() function is defined to create tables in a SQLite database (youtube_data.db) to store channel, playlist, video, and comment data.
      
      -Tables include channel, playlist, video, and comment, each with specific columns to store relevant information.
      
  #Streamlit Application:
  
  -The main() function is defined as the entry point for the Streamlit application.
  
  -It sets up the Streamlit app with three pages: "Home", "Q/A", and "Tables", using a sidebar for navigation.
  Each page offers different functionalities based on user interaction.
  
  
  #Home Page:
  
  -Allows users to input a YouTube channel ID or URL.
  
  -Upon clicking the "Retrieve Channel Data" button, it retrieves data for the specified channel using the YouTube Data API.
  
  -The retrieved data includes channel name, subscriber count, total video count, latest videos, etc., which are displayed to the user.
  
  -The data is also stored in the SQLite database using the store_channel_data() function.
  
  #Q/A Page:
  
  -Provides answers to predefined questions about the channel data stored in the database.
  
  -Users can select a question from a dropdown menu, and the corresponding answer is displayed.
  
  -Questions include queries like most viewed videos, top channels by video count, comments on videos, etc.
  
  -The answers are fetched from the SQLite database.
  
  #Tables Page:
  
  -Displays the contents of the database tables (channel, playlist, video, comment) in tabular format.
  
  -Tables are retrieved from the SQLite database and rendered using Streamlit's st.table() function.
  
  
Overall, this application serves as a comprehensive tool for analyzing YouTube channel data, offering both predefined insights and the flexibility to explore custom queries. It provides a seamless user experience through an intuitive web interface built with Streamlit.
