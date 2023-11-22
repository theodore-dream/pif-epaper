import os
import requests
import re

# Configuration options
API_KEY = os.environ["MUSIXMATCH_API_KEY"]
ARTIST = "Parcels"  # Replace with your desired artist
TITLE = "Tieduprightnow"  # Replace with your desired song title

BASE_URL = "https://api.musixmatch.com/ws/1.1/"



def get_track_id(artist: str, title: str) -> str:
    search_url = f"{BASE_URL}track.search?format=json&callback=callback&q_artist={artist}&q_track={title}&quorum_factor=1&apikey={API_KEY}"
    response = requests.get(search_url)
    track_data = response.json()

    if track_data["message"]["header"]["execute_time"] > 0:
        try:
            track_id = track_data["message"]["body"]["track_list"][0]["track"]["track_id"]
        except (IndexError, KeyError, TypeError) as e:
            return f"Error occurred while parsing track data: {e}"
        
        return track_id
    else:
        return "Track not found"

def get_song_lyrics(artist: str, title: str) -> str:
    track_id = get_track_id(artist, title)
    if track_id == "Track not found":
        return "Lyrics not found"
    else:
        lyrics_url = f"{BASE_URL}track.lyrics.get?format=json&callback=callback&track_id={track_id}&apikey={API_KEY}"
        response = requests.get(lyrics_url)
        lyrics_data = response.json()

        if lyrics_data["message"]["header"]["status_code"] == 200:
            return lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
        else:
            return "Lyrics not found"
        
def get_lyrics_only(lyrics):
    lines = lyrics.split('\n')
    return '\n'.join(lines[2:-1])

def main():
    # Use the configured artist and title
    artist = ARTIST
    title = TITLE

    lyrics = get_song_lyrics(artist, title)
    lyrics_only = get_lyrics_only(lyrics)
    print(lyrics_only)

if __name__ == "__main__":
    main()

