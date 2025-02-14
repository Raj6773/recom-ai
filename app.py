import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"  # Change this if your backend is running on another device

def get_trailer_url(movie_name):
    response = requests.get(f"{BACKEND_URL}/get_trailer?movie={movie_name}")
    data = response.json()
    if "trailer_url" in data:
        return data["trailer_url"]
    return None

st.title("Movie Recommendation System")

movies = [
    {"name": "Inception", "image": "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg"},
    {"name": "Interstellar", "image": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg"},
    {"name": "Avatar", "image": "https://upload.wikimedia.org/wikipedia/en/d/d6/Avatar_%282009_film%29_poster.jpg"}
]

for movie in movies:
    col1, col2 = st.columns([1, 3])

    with col1:
        trailer_url = get_trailer_url(movie["name"])
        if trailer_url:
            st.markdown(f"[![{movie['name']}]({movie['image']})]({trailer_url})")
        else:
            st.image(movie["image"], caption=movie["name"], use_column_width=True)

    with col2:
        st.subheader(movie["name"])
