import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import math

from credentials import cID, secret


client_credentials_manager = SpotifyClientCredentials(client_id = cID, client_secret = secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)



# Finds the lyrics of each song by finding the lyrics from Genius.com

def scrape_lyrics(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname)
    page = requests.get('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')

    for br in html('br'):
        br.replace_with(' ')
    
    lyrics1 = html.find("div", class_="lyrics")
    lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 jYfhrf")
    if lyrics1:
        lyrics = lyrics1.get_text().lower()
    elif lyrics2:
        lyrics = lyrics2.get_text().lower()
    elif lyrics1 == lyrics2 == None:
        lyrics = None

    return lyrics

def lyrics_onto_frame(df1, artist_name):
    for i,x in enumerate(df1['track']):
        test = scrape_lyrics(artist_name, x)
        df1.loc[i, 'lyrics'] = test
    return df1


# Get all the songs and song name in a playlist
# To call, need the url_info related to the spotify playlist 

def get_playlist_tracks(url_info):

    track = []
    artist = []

    offset_val = 0
    total_pre = sp.playlist_items(url_info, fields = 'total')
    total = total_pre['total']

    while offset_val < total:
        one = sp.playlist_items(url_info, fields= 'items.track.album.artists.name, items.track.name', limit=100, offset = offset_val)

        df1 = pd.DataFrame(one)

        for i, x in df1['items'].items():
            artist.append(x['track']['album']['artists'][0]['name'])
            track.append(x['track']['name'])
        
        offset_val += 100

    df2 = pd.DataFrame({
        'track':track,
        'artist':artist,
    })

    return df2


# adds lyrics onto a playlist_tracks dataframe
# call with a pandas dataframe
def lyrics_onto_playlist(df1):
    for x in df1.index:
        test = scrape_lyrics(df1['artist'][x],df1['track'][x])
        df1.loc[x, 'lyrics'] = test
    return df1



# searches through lyrics associated with the song and returns only songs that contain that lyric
# words is a list of words

def parse_for_words(df1, words):

    track = []
    artist = []

    for x in df1.index:
        for word in words:
            if not pd.isna(df1['lyrics'][x]):
                if word in df1['lyrics'][x]:
                    track.append(df1['track'][x])
                    artist.append(df1['artist'][x])
    
    df2 = pd.DataFrame({
        'name':track,
        'artist':artist
    })
    return df2


# Wrapper function to call the other 3 functions needed to find what songs contain a certain word
# from within a playlist

def lyrics_from_playlist(url_info, words):
    df1 = get_playlist_tracks(url_info)
    df2 = lyrics_onto_playlist(df1)

    df3 = parse_for_words(df2, words)

    return df3


# Merge two different pandas data frames together
def merge_frames(df1, df2):
    df3 = df1.merge(df2, left_index= True, right_index= True)
    return df3
