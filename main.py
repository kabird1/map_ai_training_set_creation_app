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
if 'user_file' not in st.session_state:
    st.session_state.user_file=None
session_token_request = requests.post('https://tile.googleapis.com/v1/createSession', params=params, headers=headers, json=json_data)
print(session_token_request.json())

st.session_state.params = {
    'session': session_token_request.json()['session'],
    'key': 'AIzaSyA4MhqXRYSOSOkfKw5vk-YYupMuYPMFcMQ',
}

if 'data' not in st.session_state:
    st.session_state.data=None
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'image_container' not in st.session_state:
    st.session_state.image_container = st.empty()


#function to load up images from google maps api:
def load_new_image():
    #returns none if all the coordinates have been shown
    if st.session_state.counter<len(st.session_state.data.x):
        x = st.session_state.data.x[st.session_state.counter]
        y = st.session_state.data.y[st.session_state.counter]
        z = 15
        url='https://tile.googleapis.com/v1/2dtiles/'+str(z)+"/"+str(x)+"/"+str(y)
        print(url)
        map = requests.get(url=url, params=st.session_state.params)
        #checks that map has any features... google api will not return maps for the ocean, only areas with features
        if map.ok:
            display_image = map.content
            with st.session_state.image_container.container():
                st.image(image=display_image, caption="Satellite image at coordinates X="+str(x)+", Y="+str(y)+", Copyright Map data ©2023")
        #if google api does not return a photo (i.e. no features at that coordinate) the csv file "features" column for that set of coordinates is set to "no"
        else:
            data_manip = st.session_state.data
            data_manip.at[st.session_state.counter, 'feature']=0
            st.session_state.data = data_manip
            print(st.session_state.data.loc[[st.session_state.counter]])
            st.session_state.counter+=1
            load_new_image()


#yes button with function to update the csv file and then load up a new image
def yes_button_callback():
    if st.session_state.user_file!=None:
        data_manip = st.session_state.data
        data_manip.at[st.session_state.counter, 'feature']=1
        st.session_state.data = data_manip
        st.session_state.counter+=1
        load_new_image()



#no button with function to update the csv file and then load up a new image
def no_button_callback():
    if st.session_state.user_file!=None:
        data_manip = st.session_state.data
        data_manip.at[st.session_state.counter, 'feature']=0
        st.session_state.data = data_manip
        st.session_state.counter+=1
        load_new_image()


#user uploads file here
#when user uploads new file, counter is reset, and the first image is loaded
st.session_state.user_file=st.file_uploader(label="Upload CSV", type={"csv","txt"}, help="CSV File containg the following columns X-coordinate, Y-Coordinate, Feature, Yes/No.")
if st.session_state.user_file!=None:
    st.session_state.data=pd.read_csv(st.session_state.user_file)
    st.data_editor(data=st.session_state.data)
    if len(st.session_state.data.x)>0:
        load_new_image()
        st.button(label="Yes", help="Yes = The feature IS shown in the image", on_click=yes_button_callback)
        st.button(label='No', help="No = The feature IS NOT shown in the image", on_click=no_button_callback)


#This takes the pandas dataframe and turns it into a CSV file, and shows a download button
if st.session_state.user_file!=None:
    output_csv = st.session_state.data.to_csv().encode('utf-8')
    st.download_button(label="Download updated CSV", data=output_csv, file_name='maps_training_data.csv', mime='text/csv')



