import json
import librosa
import numpy as np
import requests


def calculate_features(song_path, sr=22050, chunk_size=256000):

    mono_data, sr = librosa.load(song_path, mono=True, sr=sr)
    # Smooth the whole song using a moving average filter
    window_size = int(sr * 0.05)  # 50 ms window
    if window_size < 1:
        window_size = 1
    # Downsample the smoothed waveform to reduce the number of values
    smoothed_waveform = np.convolve(mono_data, np.ones(window_size)/window_size, mode='same')
    reduction_factor = 100  # Keep every 10th value (adjust as needed)
    smoothed_waveform = smoothed_waveform[::reduction_factor]
    # INSERT_YOUR_CODE
    # Ensure the smoothed waveform amplitude is relative to the original
    # (i.e., scale the smoothed waveform so its max absolute value matches the original's)
    original_max = np.max(np.abs(mono_data))
    smoothed_max = np.max(np.abs(smoothed_waveform))
    if smoothed_max > 0:
        smoothed_waveform = smoothed_waveform * (original_max / smoothed_max)

    # Convert the smoothed waveform to 16-bit integer format
    smoothed_waveform_int8 = np.int8(smoothed_waveform / np.max(np.abs(smoothed_waveform)) * 127)

    # make sure the song is 22500 sr
    num_chunks = int(np.ceil(len(mono_data) / chunk_size))

    mel_chunks = []
    chroma_chunks = []
    choma_filter = librosa.filters.chroma(sr=sr, n_fft=2048)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(mono_data))
        if i > 0:
            chunk = mono_data[start-(2048-512):end]
        else:
            chunk = mono_data[start:end]
        if i == (num_chunks - 1):
            chunk = np.pad(chunk, (0, 512*2), 'constant')
        # Perform STFT
        if i == 0:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=True,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            chroma_result = np.dot(choma_filter, np.abs(stft_result))
            mel_chunks.append(mel_result[:, :-2])
            chroma_chunks.append(chroma_result[:, :-2])

        else:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048, center=False)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=False,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            chroma_result = np.dot(choma_filter, np.abs(stft_result))
            mel_chunks.append(mel_result)
            chroma_chunks.append(chroma_result)
            
    merged_mel_spec = np.hstack(mel_chunks)
    merged_chroma_spec = np.hstack(chroma_chunks)
    # INSERT_YOUR_CODE
    merged_chroma_spec = merged_chroma_spec / np.max(merged_chroma_spec, axis=0, keepdims=True)
    # Normalize each row so the max is 1, but if the max is 0, leave the row unchanged;
    mean_chroma = np.mean(merged_chroma_spec, axis=1)

    # pitches in 12 tone equal temperament 
    pitches = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']


    # select the most dominate pitch
    pitch_id = np.argmax(mean_chroma)
    pitch = pitches[pitch_id]

    min_third_id = (pitch_id+3)%12
    maj_third_id = (pitch_id+4)%12

    #check if the musical 3rd is major or minor
    if mean_chroma[min_third_id] < mean_chroma[maj_third_id]:
        third = 'major'
    else:
        third = 'minor'

    estimated_key = pitch + ' ' + third

    return merged_mel_spec, estimated_key, smoothed_waveform_int8


def upload_to_gbp(merged_mel_spec, npy_url):

    # Upload the NPY file to the signed URL
    headers = {'Content-Type': 'application/octet-stream'}
    response2 = requests.put(npy_url, data=merged_mel_spec.tobytes(), headers=headers)
    # Check if the upload was successful
    if not response2.status_code == 200:
        raise Exception('Failed to upload features.')


def process_song(access_token, song_path, song_title, artist_name, language, genre, date_released):
    response = requests.post(
        'https://api.phiona.co.uk/api/get_new_track_upload_urls',
        json={'song_title': song_title, 'artist_name': artist_name, 'language': language, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    data = json.loads(response.content)
    track_id = data['track_id']
    npy_url = data['npy_url']
    merged_mel_spec, key, smoothed_waveform_int8 = calculate_features(song_path)
    response2 = requests.post(
        'https://api.phiona.co.uk/api/save_key',
        json={'song_id': track_id, 'key': key, 'smoothed_waveform_int8': smoothed_waveform_int8.tolist()},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )

    upload_to_gbp(merged_mel_spec, npy_url)
    return track_id


def generate_predictions(access_token, track_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_emotions',
        json={'track_id': track_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    if response.status_code == 200:
        print('predictions generation success')


def get_file_status(access_token, sorting_mechanism=[]):
    response = requests.post(
        'https://api.phiona.co.uk/api/get_files',
        json={'sorting_mechanism': sorting_mechanism},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    song_info = json.loads(response.content)['song_info']
    
    return song_info


def generate_playlist_raw(access_token, targets, age_window=None, required_duration=1800):
    vars = {'targets': targets, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_raw',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_presets(access_token, preset, required_duration=1800):
    vars = {'targets': preset, 'required_duration': required_duration}
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_presets',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_from_songs(access_token, song_ids, age_window=None, required_duration=1800):
    vars = {'song_ids': song_ids, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_songs',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_similar_songs(access_token, song_id):
    vars = {'song_id': song_id}
    response = requests.post(
        'https://api.phiona.co.uk/api/return_similar_songs',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_refresh_token(username, password):
    response = requests.post(
        'https://api.phiona.co.uk/api/token/',
        json={'username': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    refresh_token = json.loads(response.content)['refresh']
    
    return refresh_token


def get_new_access_token(refresh_token):
    response = requests.post(
        'https://api.phiona.co.uk/api/token/refresh/',
        json={'refresh': refresh_token},
        headers={'Content-Type': 'application/json'}
    )
    access_token = json.loads(response.content)['access']
    
    return access_token


def add_new_file(access_token, song_path, song_title, artist_name, language, genre, date_released):
    track_id = process_song(access_token, song_path, song_title, artist_name, language, genre, date_released)
    generate_predictions(access_token, track_id)


def edit_song(access_token, song_id, song_title, artist_name, genre, date_released):
    response = requests.post(
        'https://api.phiona.co.uk/api/edit_song',
        json={'song_id': song_id, 'song_title': song_title, 'artist_name': artist_name, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def edit_user_playlist(access_token, playlist_id, new_playlist_name):
    response = requests.post(
        'https://api.phiona.co.uk/api/edit_user_playlist',
        json={'playlist_id': playlist_id, 'playlist_name': new_playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_song(access_token, song_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_song',
        json={'song_id': song_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_user_playlist(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_user_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_generated_playlist(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_generated_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def create_new_playlist(access_token, playlist_name):
    response = requests.post(
        'https://api.phiona.co.uk/api/create_new_playlist',
        json={'playlist_name': playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def add_song_to_playlist(access_token, playlist_id, song_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/add_song_to_playlist',
        json={'song_id': song_id, 'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def load_user_playlists(access_token):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_user_playlists',
        json={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['playlists_info']


def load_generated_playlists(access_token):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_generated_playlists',
        json={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['generated_playlists_info']



def load_user_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_user_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']


def load_generated_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_generated_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']


def get_artists(access_token, sorting_mechanism=[]):
    response = requests.post(
        'https://api.phiona.co.uk/api/get_artists',
        json={'sorting_mechanism': sorting_mechanism},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'   
        }
    )
    artist_info = json.loads(response.content)['artist_info']
    
    return artist_info


def get_similar_artists(access_token, artist_id, n_max_artists=10, genre='all'):
    vars = {'artist_id': artist_id, 'n_max_artists': n_max_artists, 'genre': genre}
    response = requests.post(
        'https://api.phiona.co.uk/api/return_similar_artists',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    artist_info = json.loads(response.content)
    
    return artist_info


def multi_target_playlist_creation(access_token, targets):
    vars = {'targets': targets}
    response = requests.post(
        'http://localhost:8000/api/multi_target_playlist_creation',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info
