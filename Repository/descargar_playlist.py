'''Overview This Python program allows you to download the audio tracks from a Spotify playlist. It utilizes the
Spotify API to fetch the playlist information and the yt-dlp library to download the audio tracks from YouTube.

Features
Supports downloading tracks from any public Spotify playlist.
Provides a graphical user interface (GUI) built with Tkinter for easy interaction.
Shows progress bars for individual track downloads and overall playlist download progress.
Allows cancellation of the download process.
Prerequisites
Before running the program, make sure you have the following installed:

Python 3.x
Required Python packages: spotipy, yt-dlp, tkinter, threafing, re, os

Author
Fabian
GitHub: fa8i
'''

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import re
import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import yt_dlp


para_llorar = 'https://open.spotify.com/playlist/3bM9My07AYO4L1V4eh2T1B?si=1b565eb47dca493f'
espanolas_tristes = 'https://open.spotify.com/playlist/0etpTeyavVvvR9M7a9bWRZ?si=7fee005c3aee4e34'
espanolas_tristes2 = 'https://open.spotify.com/playlist/69d0HOCdiNeGt41wYx58tn?si=28a0c6204b6e4c30'
espanolas_tristes3 = 'https://open.spotify.com/playlist/7xB7IeYHpZd5X6u54Ki7sA?si=e3c309bf7a3c4cbc'

alegres_espanol = 'https://open.spotify.com/playlist/0YNYXKVB5Kp7mQUYwZexxU?si=bff3e039dfb74263'
alegres_espanol2 = 'https://open.spotify.com/playlist/7lgD1adftkv6QGOD4TCeZq?si=8589442d23e347d3'
alegres_espanol3 = 'https://open.spotify.com/playlist/3shawWHDZK6CVgRZmUj63S?si=b6f15ef73fd44be3'
reggaeton1 = 'https://open.spotify.com/playlist/70qjH9AXW7yvBvK1uKAIyv?si=ed042c0ddd6a480f'


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Descargar Playlist")

        self.frame_ingreso = tk.Frame(self)
        self.frame_ingreso.pack(padx=10, pady=10)

        tk.Label(self.frame_ingreso, text="URL Playlist Spotify:").grid(row=0, column=0, sticky="w")
        tk.Label(self.frame_ingreso, text="Ruta de Descarga:").grid(row=1, column=0, sticky="w")

        self.entrada_url = tk.Entry(self.frame_ingreso, width=50)
        self.entrada_url.grid(row=0, column=1, padx=5, pady=5)

        self.entrada_ruta = tk.Entry(self.frame_ingreso, width=50)
        self.entrada_ruta.grid(row=1, column=1, padx=5, pady=5)

        self.boton_seleccionar_ruta = tk.Button(self.frame_ingreso, text="Seleccionar Ruta",
												command=self.seleccionar_ruta_descarga)
        self.boton_seleccionar_ruta.grid(row=1, column=2, padx=5, pady=5)

        self.boton_descargar = tk.Button(self.frame_ingreso, text="Descargar Lista", command=self.ejecutar_programa)
        self.boton_descargar.grid(row=2, column=1, pady=10)

        self.frame_descarga = tk.Frame(self)
        self.lista_canciones = tk.Listbox(self.frame_descarga, width=50)
        self.progress_bar_cancion = ttk.Progressbar(self.frame_descarga, orient="horizontal", length=300,
													mode="determinate")
        self.progress_bar_total = ttk.Progressbar(self.frame_descarga, orient="horizontal", length=300,
												  mode="determinate")

        self.label_cancion = tk.Label(self.frame_descarga, text="", anchor="w")
        self.label_cancion.pack(fill="x")
        self.progress_bar_cancion.pack(pady=5)

        # Crear la etiqueta para el progreso total y mostrarla
        self.label_barra_total = tk.Label(self.frame_descarga, text="")
        self.label_barra_total.pack(fill="x", pady=5)
        self.progress_bar_total.pack(pady=5)

        self.boton_cancelar = tk.Button(self.frame_descarga, text="Cancelar", command=self.cancelar_descarga)
        self.boton_cancelar.pack(pady=10)

        self.client_id = 'YOUR_CLIENT_ID'         
        self.client_secret = 'YOUR_CLIENT_SECRET'     
        self.client_credentials_manager = SpotifyClientCredentials(client_id=self.client_id,
																   client_secret=self.client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

        self.descarga_en_progreso = False
        self.tracks = []

    def seleccionar_ruta_descarga(self):
        ruta_descarga = filedialog.askdirectory()
        self.entrada_ruta.delete(0, tk.END)
        self.entrada_ruta.insert(0, ruta_descarga)

    def ejecutar_programa(self):
        if not self.descarga_en_progreso:
            self.frame_ingreso.pack_forget()  
            self.frame_descarga.pack(padx=10, pady=10)  

            url_playlist = self.entrada_url.get()
            playlist_id = re.search(r'playlist\/(\w{22})', url_playlist).group(1)
            output_folder = self.entrada_ruta.get()

            self.descarga_en_progreso = True
            self.tracks = self.obtener_tracks_playlist(playlist_id)
            threading.Thread(target=self.descargar_canciones, args=(output_folder,)).start()

    def cancelar_descarga(self):
        if self.descarga_en_progreso:
            self.descarga_en_progreso = False
            self.frame_descarga.pack_forget()
            self.frame_ingreso.pack()

    def obtener_tracks_playlist(self, playlist_id):
        tracks = []
        offset = 0
        while True:
            results = self.sp.playlist_tracks(playlist_id, offset=offset)
            items = results.get('items', [])
            if not items:
                break
            for item in items:
                track = item.get('track')
                if track:
                    tracks.append((track.get('name', ''), track.get('artists', [{}])[0].get('name', '')))
            offset += len(items)
        return tracks

    def download_audio(self, link, output_folder, song_name, artist):
        if not self.descarga_en_progreso:
            return

        file_name = f"{song_name} - {artist}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_folder, file_name),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        self.lista_canciones.insert(tk.END, f"{song_name} - {artist}")
        self.progress_bar_cancion.stop()

    def descargar_canciones(self, output_folder):
        total_tracks = len(self.tracks)
        tracks_downloaded = 0

        for i, track in enumerate(self.tracks):
            if not self.descarga_en_progreso:
                break

            song_name, artist = track
            search_query = f"{song_name} {artist} audio"
            link = f"ytsearch1:{search_query}"
            self.label_cancion.config(text=f"Descargando: {song_name} - {artist}")
            self.progress_bar_cancion.start()
            self.download_audio(link, output_folder, song_name, artist)
            tracks_downloaded += 1
            porcentaje_total = 100 * tracks_downloaded / total_tracks
            self.progress_bar_total['value'] = porcentaje_total
            self.progress_bar_cancion['value'] = 0

            # Actualizar el texto de la barra de progreso total
            texto_barra_total = f"Descargadas {tracks_downloaded} canciones de {total_tracks} ({porcentaje_total:.2f}%)"
            self.label_barra_total.config(text=texto_barra_total)

        self.cancelar_descarga()

ventana = VentanaPrincipal()
ventana.mainloop()

