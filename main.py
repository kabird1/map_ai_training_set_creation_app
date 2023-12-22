import streamlit as st
import requests
import pandas as pd

headers = {
    'Content-Type': 'application/json',
}

params = {
    'key': 'AIzaSyA4MhqXRYSOSOkfKw5vk-YYupMuYPMFcMQ',
}

json_data = {
    'mapType': 'satellite',
    'language': 'en-US',
    'region': 'US',
}
user_file=None
session_token_request = requests.post('https://tile.googleapis.com/v1/createSession', params=params, headers=headers, json=json_data)
print(session_token_request.json())

#function to load up images from google maps api:
def load_new_image():
    global display_image
    global counter
    global data
    #returns none if all the coordinates have been shown
    if counter<len(data.x):
        x = data.x[counter]
        y = data.y[counter]
        z = 15
        url='https://tile.googleapis.com/v1/2dtiles/'+str(z)+"/"+str(x)+"/"+str(y)
        print(url)
        map = requests.get(url=url, params=params)
        #checks that map has any features... google api will not return maps for the ocean, only areas with features
        if map.ok:
            display_image = map.content
        #if google api does not return a photo (i.e. no features at that coordinate) the csv file "features" column for that set of coordinates is set to "no"
        else:
            data.feature[counter]='no'
            print(data.loc[[counter]])
            counter=counter+1
            load_new_image()
    else:
        display_image=None


#yes button with function to update the csv file and then load up a new image
def yes_button_callback():
    global counter
    global data
    if user_file!=None:
        data.feature[counter]='yes'
        counter=counter+1
        load_new_image()
st.button(label='Yes', help='Yes = The feature IS shown in the image', on_click=yes_button_callback)


#no button with function to update the csv file and then load up a new image
def no_button_callback():
    global counter
    global data
    if user_file!=None:
        data.feature[counter]='no'
        counter=counter+1
        load_new_image()
st.button(label='No', help="No = The feature IS NOT shown in the image", on_click=no_button_callback)


#user uploads file here
#when user uploads new file, counter is reset, and the first image is loaded
def new_file_uploaded():
    global counter
    global data
    global user_file
    data=pd.read_csv(user_file)
    counter = 0
    load_new_image()
user_file=st.file_uploader(label="Upload CSV", type={"csv","txt"}, help="CSV File containg the following columns X-coordinate, Y-Coordinate, Feature, Yes/No.", on_change=new_file_uploaded)



#This button takes the pandas dataframe and turns it into a CSV file, then shows a download button
def update_file_callback():
    if user_file!=None:
        output_csv = data.to_csv().encode('utf-8')
        st.download_button(label="Download updated CSV", data=output_csv, file_name='maps_training_data.csv', mime='text/csv')
st.button(label="Update my .csv file", help="Updates the CSV file with your yes and no answers", on_click=update_file_callback)










