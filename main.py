import streamlit as st
import requests

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

session_token_request = requests.post('https://tile.googleapis.com/v1/createSession', params=params, headers=headers, json=json_data)
print(session_token_request.json())


params = {
    'session': session_token_request.json()['session'],
    'key': 'AIzaSyA4MhqXRYSOSOkfKw5vk-YYupMuYPMFcMQ',
}

x=6294
y=13288
z=15

url='https://tile.googleapis.com/v1/2dtiles/'+str(z)+"/"+str(x)+"/"+str(y)
print(url)

map = requests.get(url=url, params=params)
print(map)
print(map.content)

with open('Training data from satellite images app/example_tile.png', 'wb') as f:
    f.write(map.content)

st.button(label='Yes', help='Yes = The feature IS shown in the image')
st.button(label='No', help="No = The feature IS NOT shown in the image")



