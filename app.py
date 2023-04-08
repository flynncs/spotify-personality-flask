import os
import config
from flask import Flask, request, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import openai

app = Flask(__name__)

# Set the openai api key
openai.api_key = os.environ['OPENAI_API_KEY']

# Home page with login button
@app.route('/')
def index():
    personality_analysis = None
    if 'access_token' in request.cookies:
        sp = spotipy.Spotify(auth=request.cookies.get('access_token'))
        top_artists = sp.current_user_top_artists(time_range='medium_term', limit=5)
        artist_names = [artist['name'] for artist in top_artists['items']]
        print(artist_names)
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"I listen to {', '.join(name for name in artist_names)}. For each artist, draw a negative conclusion on my personality. List controversies surrounding my chosen artists. Finally, provide a summary of my likely negative personality traits. Format this in a conversational way, and scatter personal insults throughout.",
            max_tokens=1000
        )
        personality_analysis = completion.choices[0].text
        
    return render_template('home.html', personality_analysis=personality_analysis)
 
# Login with Spotify
@app.route('/login')
def login():
    auth_manager = SpotifyOAuth(scope='user-top-read')
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

# Callback after login
@app.route('/callback')
def callback():
    auth_manager = SpotifyOAuth(scope='user-top-read')
    if request.args.get('code'):
        auth_manager.get_access_token(request.args.get('code'))
        response = redirect('/')
        response.set_cookie('access_token', auth_manager.get_access_token()['access_token'])
        return response
    else:
        return redirect('/')
