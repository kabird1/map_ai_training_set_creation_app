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
    'scale': 'scaleFactor4x',
    'highDpi': 'true'
}
if 'user_file' not in st.session_state:
    st.session_state.user_file=None
session_token_request = requests.post('https://tile.googleapis.com/v1/createSession', params=params, headers=headers, json=json_data)
print(session_token_request.json())

st.session_state.params = {
    'session': session_token_request.json()['session'],
    'key': str(st.secrets["key"]),
}

if 'data' not in st.session_state:
    st.session_state.data=None
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'answer' not in st.session_state:
    st.session_state.answer = None
if 'comments' not in st.session_state:
    st.session_state.comments=None
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
st.session_state.image_container = st.empty()

help=st.expander("Help")
help.write('The purpose of this app is to generate a data set to train an AI model to identify features on satellite images of maps.')
help.write('1.Create .csv file with columns \"x\" and \"y\".')
help.write('2. Populate with x and y coordinates of locations on the maps. For information on how to enter coordinates see https://developers.google.com/maps/documentation/javascript/coordinates. The app is set to use zoom setting 19.')
help.write('3. Upload the .csv file to the app, using the browse button, or by dragging and dropping your file.')
help.write('4. The contents of the .csv file are displayed at the bottom of the screen. The user can edit the data by clicking on cells and typing, and can download the edited data at any time.')
help.write('5. Satellite images of the locations are loaded by Google Maps API and displayed on the screen. Underneath the image, the user can enter their input using the three buttons: Yes, No and Inconclusive. The user can also enter any addition comments.')
help.write('6. Upon pressing the submit button, the Yes/No/Inconclusive selection is entered under the \'features\' column appended to the user\'s .csv file. The comments entered in the textbox are entered under the \'comments\' column appended to the user\'s .csv file')
help.write('5. Google Maps API does not return images for locations that contain no features \"i.e. the middle of the ocean\". In these cases, \'features\' column will be marked with a \'No\' answer, and the comments column will contain an explanation')
help.write('6. The annotated coordinates file can be downloaded and can be used to train an AI model.')

#function to load up images from google maps api:
def load_new_image():
    st.session_state.answer = None
    st.session_state.comments=None
    #returns none if all the coordinates have been shown
    if st.session_state.counter<len(st.session_state.data.x):
        x = st.session_state.data.x[st.session_state.counter]
        y = st.session_state.data.y[st.session_state.counter]
        z = 19
        url='https://tile.googleapis.com/v1/2dtiles/'+str(z)+"/"+str(x)+"/"+str(y)
        print(url)
        map = requests.get(url=url, params=st.session_state.params)
        #checks that map has any features... google api will not return maps for the ocean, only areas with features
        if map.ok:
            display_image = map.content
            st.session_state.image_container.image(image=display_image, caption="Satellite image at coordinates X="+str(x)+", Y="+str(y)+", Copyright Map data ©2023")
        #if google api does not return a photo (i.e. no features at that coordinate) the csv file "features" column for that set of coordinates is set to "no"
        else:
            st.session_state.data.at[st.session_state.counter, 'feature']='No'
            st.session_state.data.at[st.session_state.counter, 'comments']='The Google Maps Tiles API did not return an image for this set of coordinates. Google Maps Tiles API does not return images for coordinates that do not contain features, such as images of only blue ocean'
            print(st.session_state.data.loc[[st.session_state.counter]])
            st.session_state.counter+=1
            load_new_image()
    else:
        with st.session_state.image_container.container():
            st.write("You've reached the end of the data set")


#yes button with function to update the csv file and then load up a new image
def yes_button_callback():
    st.session_state.answer=1
    st.session_state.button_clicked=True


#no button with function to update the csv file and then load up a new image
def no_button_callback():
    st.session_state.answer='No'
    st.session_state.button_clicked=True

def inc_button_callback():
    st.session_state.answer = 'Yes'

def submit_button_callback():
    st.session_state.data.at[st.session_state.counter, 'feature']=st.session_state.answer
    st.session_state.data.at[st.session_state.counter, 'comments']=st.session_state.comments
    st.session_state.counter+=1
    load_new_image()

#user uploads file here
#when user uploads new file, counter is reset, and the first image is loaded

if st.session_state.user_file==None:
    st.session_state.user_file=st.file_uploader(label="Upload CSV", type={"csv","txt"}, help="CSV File containg the following columns X-coordinate, Y-Coordinate, Feature, Yes/No.")

if st.session_state.user_file!=None:
    if st.session_state.counter==0 and st.session_state.button_clicked==False:
        st.session_state.data=pd.read_csv(st.session_state.user_file)
        st.session_state.data.at[st.session_state.counter, 'feature']=''
        st.session_state.data.at[st.session_state.counter, 'comments']=''
    if len(st.session_state.data.x)>0:
        load_new_image()
        col1, col2, col3= st.columns(3)
        col1.button(label="Yes", help="Yes = The feature IS shown in the image", on_click=yes_button_callback, use_container_width=True)
        col2.button(label='No', help="No = The feature IS NOT shown in the image", on_click=no_button_callback, use_container_width=True)
        col3.button(label="Inconclusive", help = "Inconclusive = Unsure if feature is shown in the image", on_click=inc_button_callback, use_container_width=True)
        st.session_state.comments = st.text_area(label="Comments", label_visibility="hidden", placeholder="Enter your comments here")
        st.button(label="Submit", help="Submit the data, update the .csv file and move to the next image", on_click=submit_button_callback, use_container_width=True)
        st.data_editor(data=st.session_state.data, use_container_width=True)


