from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

YOUTUBE_API_KEY = "AIzaSyCcFpGDC3yY4yOpZJPJdvbUSfGIDQ0vQdE"  # Replace with your valid API key

@app.route("/get_trailer", methods=["GET"])
def get_trailer():
    movie_name = request.args.get("movie")
    if not movie_name:
        return jsonify({"error": "Movie name is required"}), 400

    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{movie_name} official trailer",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    # 🔴 PRINT the full response to debug errors
    print("YouTube API Response:", data)

    if "items" in data and len(data["items"]) > 0:
        video_id = data["items"][0]["id"]["videoId"]
        trailer_url = f"https://www.youtube.com/watch?v={video_id}"
        return jsonify({"trailer_url": trailer_url})

    return jsonify({"error": "Trailer not found", "response": data}), 404

if __name__ == "__main__":
    print("Flask server is starting...")
    app.run(debug=True, port=5000)
