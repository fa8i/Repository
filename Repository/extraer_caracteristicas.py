import librosa
import numpy as np
import pandas as pd
import os
import shutil

# Seleccionar 1 para playlist alegre, 0 para playlist triste
ALEGRE_TRISTE = 1

# Extraer las caracteristicas ed cada cancion
def extract_musical_features(song_path):
    try:
        # Cargar cancion con librosa
        y, sr = librosa.load(song_path)

        # Extraer características musicales
        tempo = librosa.beat.tempo(y=y, sr=sr)
        tonality = librosa.feature.chroma_stft(y=y, sr=sr)

        # Características adicionales
        rms = librosa.feature.rms(y=y)
        zcr = librosa.feature.zero_crossing_rate(y=y)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        mfcc_promedio = np.mean(mfcc, axis=1)
        mfcc_mediana = np.median(mfcc, axis=1)
        mfcc_desviacion_estandar = np.std(mfcc, axis=1)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        pitch, _ = librosa.piptrack(y=y, sr=sr)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)


        #Separar el nombre  y el artista
        nombre_archivo = os.path.splitext(os.path.basename(song_path))[0]
        nombre_cancion, *resto = nombre_archivo.split(" - ")
        nombre_artista = resto[0][:-4] if resto and resto[0].endswith('.mp3') else (resto[0] if resto else None)

        # Guardar las características en un diccionario
        features = {
            'Nombre': nombre_cancion,
            'Artista': nombre_artista,
            'Tempo': tempo[0],
            'Tonalidad_1': tonality,
            'RMS_Energy': rms.mean(),
            'Zero_Crossing_Rate': zcr.mean(),
            'Pitch': pitch.mean(),
            'MFCC_1': mfcc[0].mean(),
            'MFCC_2': mfcc[1].mean(),
            'MFCC_3': mfcc[2].mean(),
            'Spectral_Centroid': spectral_centroid.mean(),
            'Spectral_Bandwidth': spectral_bandwidth.mean()
        }

        return features
    except Exception as e:
        print(f"Error processing song {song_path}: {e}")
        return None

# Directorio donde se encuentran las canciones
songs_directory = r'YOUR_DIRECTORY'
total_songs = len([song for song in os.listdir(songs_directory) if song.endswith('.mp3')])
songs_analyzed = 0
songs_features = []

# Nombre de archivo para las características parciales
partial_save_path = r'YOUR_PATH.csv'

try:
    # Extraer características de cada canción
    for song in os.listdir(songs_directory):
        if song.endswith('.mp3'):
            song_path = os.path.join(songs_directory, song)
            features = extract_musical_features(song_path)
            if features:
                features['Lable_sent'] = ALEGRE_TRISTE
                songs_features.append(features)
                songs_analyzed += 1
                print(f"Se han analizado {songs_analyzed} canciones de {total_songs} ({100 * songs_analyzed / total_songs:.2f}%)")
                # Guardar resultados parciales en un archivo CSV
                partial_df = pd.DataFrame(songs_features)
                partial_df.to_csv(partial_save_path, index=False)

except Exception as e:
    print(f"Se produjo un error durante el procesamiento: {str(e)}")

else:
    # Si no hay excepciones, mover el archivo de características parciales al archivo final
    save_path = r'YOUR_PATH_NEW.csv'
    shutil.move(partial_save_path, save_path)
    print(f"Extracción de características musicales completa. Se ha guardado el archivo final en {save_path}")

finally:
    # Eliminar el archivo de características parciales si existe
    if os.path.exists(partial_save_path):
        os.remove(partial_save_path)