import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset (Using TMDb 5000 Movie Dataset)
@st.cache_data
import ast  # Import for converting string to list

def convert_genres(genre_str):
    if isinstance(genre_str, str):  # Ensure it's a string
        genres = genre_str.split(", ")
        return str([{"id": i, "name": g} for i, g in enumerate(genres, start=1000)])
    return "[]"

@st.cache_data
def load_data():
    df = pd.read_csv("tmdb_5000_movies.csv")
    df = df.dropna(subset=['overview'])

    telugu_df = pd.read_csv(r"C:\Users\rajki\Downloads\akhila\telugu_movies.csv")
    telugu_df = telugu_df.dropna(subset=['title'])

    # Assign unique IDs if missing
    if 'id' not in telugu_df.columns:
        telugu_df["id"] = range(900000, 900000 + len(telugu_df))

    # Convert genres to TMDb format
    telugu_df["genres"] = telugu_df["genres"].apply(convert_genres)

    # Set Telugu language code
    telugu_df["original_language"] = "te"

    df = pd.concat([df, telugu_df], ignore_index=True)
    return df

movies = load_data()

# TMDb API key
API_KEY = "c2af6ea02a4f25432f8c710e134fad3d"
HEADERS = {"Accept": "application/json"}

# Compute TF-IDF similarity
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(movies["overview"])
similarity_matrix = cosine_similarity(tfidf_matrix)

def fetch_movie_details(movie_id):
    if pd.isna(movie_id):
        return {}

    # Try fetching from TMDb API
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        # If API fails, return local dataset info
        movie = movies[movies["id"] == movie_id].iloc[0]
        return {
            "title": movie["title"],
            "overview": movie["overview"],
            "poster_path": "",
            "vote_average": movie.get("vote_average", "N/A"),
            "release_date": str(movie.get("release_year", "Unknown")),
        }

def fetch_movie_cast(movie_id):
    if pd.isna(movie_id):
        return {}
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}/credits?api_key={API_KEY}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.write(f"Error fetching cast for movie {movie_id}: {e}")
        return {}

# Streamlit UI
st.title("Movie Recommendation System")
st.write("Browse movies by category, language, or search for similar ones.")

# Extract genres
def extract_genres(genre_str):
    try:
        genres = eval(genre_str)  # Convert string representation of list to actual list
        return [g["name"] for g in genres]
    except:
        return []

movies["genres_list"] = movies["genres"].apply(extract_genres)
all_genres = sorted(set(g for genre_list in movies["genres_list"] for g in genre_list))

# Extract languages
language_map = {"en": "English", "hi": "Hindi", "te": "Telugu"}
languages = ["English", "Hindi", "Telugu"]
st.write("### Filter Movies by Genre and Language")

# Select category
genre_choice = st.selectbox("Choose a genre", ["All"] + all_genres)
language_choice = st.selectbox("Choose a language", ["All"] + languages)

filtered_movies = movies
if genre_choice != "All":
    filtered_movies = filtered_movies[filtered_movies["genres_list"].apply(lambda x: genre_choice in x)]
if language_choice != "All":
    language_code = [key for key, value in language_map.items() if value == language_choice][0]
    filtered_movies = filtered_movies[filtered_movies["original_language"] == language_code]

# Search functionality
search_query = st.text_input("Search for a movie")
if search_query:
    search_results = movies[movies["title"].str.contains(search_query, case=False, na=False)]
    if not search_results.empty:
        filtered_movies = search_results
    
# Sort by rating when filtering by genre
if genre_choice != "All":
    filtered_movies = filtered_movies.sort_values(by="vote_average", ascending=False)

st.write("### Movies:")
cols = st.columns(3)
for idx, (_, row) in enumerate(filtered_movies.iterrows()):
    movie_id = row["id"]
    movie_details = fetch_movie_details(movie_id)
    if not movie_details:
        continue
    
    image_url = f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path', '')}" if movie_details.get('poster_path') else "https://via.placeholder.com/150"
    rating = movie_details.get("vote_average", "N/A")
    release_date = movie_details.get("release_date", "Unknown Year")
    cast_data = fetch_movie_cast(movie_id)
    cast_list = [cast['name'] for cast in cast_data.get("cast", [])[:3]]
    cast_names = ", ".join(cast_list)
    
    with cols[idx % 3]:
        st.image(image_url, width=150)
        st.write(f"**{row['title']} ({release_date[:4]})**")
        st.write(f"⭐ Rating: {rating}")
        st.write(f"🎭 Cast: {cast_names}")
        st.write(f"📜 Description: {row['overview'][:150]}...")
        trailer_url = f"https://www.youtube.com/results?search_query={row['title'].replace(' ', '+')}+trailer"
        if st.button(f"Watch Trailer for {row['title']}"):
            st.markdown(f"[Click here to watch the trailer]({trailer_url})", unsafe_allow_html=True)
def load_data():
    df = pd.read_csv("tmdb_5000_movies.csv")
    df = df.dropna(subset=['overview'])

    # Load Telugu movies dataset
    telugu_df = pd.read_csv(r"C:\Users\rajki\Downloads\akhila\telugu_movies.csv")
    telugu_df = telugu_df.dropna(subset=['title'])
    
    # Ensure 'id' column is present
    if 'id' not in telugu_df.columns:
        telugu_df["id"] = range(900000, 900000 + len(telugu_df))  # Assign unique IDs
    
    # Add 'original_language' column as 'te' for Telugu movies
    telugu_df["original_language"] = "te"
    
    df = pd.concat([df, telugu_df], ignore_index=True)
    return df
