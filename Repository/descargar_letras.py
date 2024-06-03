
'''
Some playlist used for training model:
para_llorar = https://open.spotify.com/playlist/3bM9My07AYO4L1V4eh2T1B?si=1b565eb47dca493f
espanolas_tristes = https://open.spotify.com/playlist/0etpTeyavVvvR9M7a9bWRZ?si=7fee005c3aee4e34
espanolas_tristes2 = https://open.spotify.com/playlist/69d0HOCdiNeGt41wYx58tn?si=28a0c6204b6e4c30
espanolas_tristes3 = https://open.spotify.com/playlist/7xB7IeYHpZd5X6u54Ki7sA?si=e3c309bf7a3c4cbc

alegres_espanol = https://open.spotify.com/playlist/0YNYXKVB5Kp7mQUYwZexxU?si=bff3e039dfb74263
alegres_espanol2 = https://open.spotify.com/playlist/7lgD1adftkv6QGOD4TCeZq?si=8589442d23e347d3
alegres_espanol3 = https://open.spotify.com/playlist/3shawWHDZK6CVgRZmUj63S?si=b6f15ef73fd44be3
reggaeton1 = https://open.spotify.com/playlist/70qjH9AXW7yvBvK1uKAIyv?si=ed042c0ddd6a480f
'''

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import re
import pandas as pd


url_spotify = 'https://open.spotify.com/playlist/3bM9My07AYO4L1V4eh2T1B?si=1b565eb47dca493f'
client_id_spotify = 'CLIENT_ID_KEY'
client_secret_spotify = 'CLIENT_SECRET_KEY'
access_token_genius = 'Bearer YOUR_GENIUS_API_KEY'


def obtener_tracks_playlist(playlist_id):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id_spotify, client_secret=client_secret_spotify)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    tracks = []
    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)
        items = results.get('items', [])
        if not items:
            break
        for item in items:
            track = item.get('track')
            if track:
                tracks.append((track.get('name', ''), track.get('artists', [{}])[0].get('name', '')))
        offset += len(items)
    return tracks


def tracks_cleaner(tracks):
    clean_tracks = []
    for cancion, artista in tracks:
        separators = [" - ", " [", " ("]
        for separator in separators:
            if separator in cancion:
                cancion = cancion.split(separator)[0]
                break

        clean_tracks.append((cancion, artista))

    return clean_tracks


def get_lyrics(song_title, artist_name):
    try:
        genius = lyricsgenius.Genius(access_token_genius)
        song = genius.search_song(song_title, artist_name)

        if song:
            return song.lyrics
        else:
            print(f"No se encontró la letra para '{song_title}' por {artist_name}.")
            return None
    except Exception as e:
        print(f"Error al buscar la letra de '{song_title}' por {artist_name}: {e}")
        return None


def limpiar_letra_cancion(texto):
    inicio_letra = re.search(r"\[.*?\]", texto)
    if inicio_letra:
        inicio_letra = inicio_letra.start()
    else:
        inicio_letra = 0

    texto = texto[inicio_letra:]
    texto = re.sub(r"\[.*?\]", "", texto)  # Eliminar secciones entre corchetes
    texto = re.sub(r"\(.*?\)", "", texto)  # Eliminar secciones entre paréntesis
    texto = re.sub(r"\*.*?\*", "", texto)  # Eliminar secciones entre asteriscos
    texto = re.sub(r"\n{2,}", "\n", texto)  # Eliminar líneas vacías duplicadas
    texto = texto.strip()  # Eliminar espacios en blanco al inicio y al final

    if texto.endswith("Embed"):
        texto = texto[:-len("Embed")].strip()

    texto = re.sub(r"\d+$", "", texto.strip())
    see_regex = re.compile(r'\nSee.*?\n')
    texto = see_regex.sub('\n', texto)
    contributors_regex = re.compile(r'.*?contributors', re.IGNORECASE)
    texto = contributors_regex.sub('', texto)
    contributor_regex = re.compile(r'.*?contributor', re.IGNORECASE)
    texto = contributor_regex.sub('', texto)
    texto = texto.replace("You might also like", "")
    texto = texto.replace("\n", " ")
    return texto


def main():
    playlist_id = re.search(r'playlist\/(\w{22})', url_spotify).group(1)
    songs0 = obtener_tracks_playlist(playlist_id)
    songs = tracks_cleaner(songs0)
    data = []
    for song in songs:
        title, artist = song
        lyrics0 = get_lyrics(title, artist)
        if lyrics0:
            lyrics = limpiar_letra_cancion(lyrics0)
            data.append([title, artist, lyrics])
        else:
            pass

    df = pd.DataFrame(data, columns=['Canción', 'Artista', 'Letra'])
    print(df)
    save_path = r'YOUR_PATH.csv'
    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    main()
