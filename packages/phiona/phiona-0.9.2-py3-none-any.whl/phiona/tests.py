import time
import datetime as dt
from phiona import (
    get_refresh_token,
    get_new_access_token,
    get_file_status,
    generate_playlist_raw,
    generate_playlist_from_songs,
    generate_playlist_presets,
    get_similar_songs,
    add_new_file,
    edit_song,
    edit_user_playlist,
    delete_song,
    delete_user_playlist,
    delete_generated_playlist,
    create_new_playlist,
    add_song_to_playlist,
    load_user_playlist_songs,
    load_generated_playlists,
    load_generated_playlist_songs,
    load_user_playlists,
    get_artists,
    get_similar_artists,
    multi_target_playlist_creation,
)

# generate access and refresh token
username = 'testaccount1'
password = '76UiSPukuf9eNXO'
# refresh token lasts for 1 week
refresh_token = get_refresh_token(username, password)
print(refresh_token)
# access token lasts for 4 hours
access_token = get_new_access_token(refresh_token)
print('access')
print(access_token)

# feed the access token to the api call

# start_time = time.time()
# track_id = add_new_file(access_token, r"C:\Users\Carl\Downloads\drive-download-20250603T085118Z-1-001\Misery Business - Paramore.mp3", 'BP', 'Paramore', '', '', '')
# process_time = time.time() - start_time
# print(f"Process song time: {process_time:.2f} seconds")


# start_time = time.time()
# song_info = get_file_status(access_token)
# status_time = time.time() - start_time
# print(f"Get file status time: {status_time:.2f} seconds")

# # get the file status but sorted
# start_time = time.time()
# song_info = get_file_status(access_token, sorting_mechanism=['-friendship_love', 'frustration'])
# status_time = time.time() - start_time
# print(f"Get file status time: {status_time:.2f} seconds")


# # generate a playlist 
# # single hybrid
# targets1 = [
#     {
#         'genre': 'Dance Pop',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '100', 
#         'avg_date': '2018-12-12',
#     },
# ]
# # multi hybrid
# targets2 = [
#     {
#         'genre': 'Dance Pop',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '60', 
#         'avg_date': '2018-12-12',
#     },
#     {
#         'genre': 'House',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '40', 
#         'avg_date': '2022-12-12',
#     },
# ]

# start_time = time.time()
# playlist_info = generate_playlist_raw(access_token, targets2)
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")

# # start_time = time.time()
# # playlist_info2 = generate_playlist_presets(access_token, 'fitness-pop')
# # status_time = time.time() - start_time
# # print(f"Get playlist status time: {status_time:.2f} seconds")

# # song_ids = [53, 54, 55, 56, 57]

# # start_time = time.time()
# # playlist_info = generate_playlist_from_songs(access_token, song_ids)
# # status_time = time.time() - start_time
# # print(f"Get playlist status time: {status_time:.2f} seconds")


# # song_ids = [56]

# # start_time = time.time()
# # playlist_info = generate_playlist_from_songs(access_token, song_ids)
# # status_time = time.time() - start_time
# # print(f"Get playlist status time: {status_time:.2f} seconds")


# song_id = 56

# start_time = time.time()
# playlist_info = get_similar_songs(access_token, song_id)
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")

# song_id = playlist_info['song_info'][-1]['id']

# out = edit_song(access_token, song_id, 'new_title', 'new_artists', 'new_genre', '2002-02-02')

# out = load_user_playlists(access_token)

# playlist_id = out[0]['id']
# import random
# import string
# random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
# out = create_new_playlist(access_token, random_name)

# random_name2 = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
# out = edit_user_playlist(access_token, playlist_id, random_name2)

# out = add_song_to_playlist(access_token, playlist_id, song_id)

# out = load_user_playlist_songs(access_token, playlist_id)

# out = delete_user_playlist(access_token, playlist_id)

# out = delete_song(access_token, song_id)

# out = load_generated_playlists(access_token)

# playlist_id = out[0]['id']

# out = load_generated_playlist_songs(access_token, playlist_id)

# out = delete_generated_playlist(access_token, playlist_id)

# out = get_artists(access_token)

# artist_id = out[0]['id']

# out2 = get_similar_artists(access_token, artist_id)

multi_targets = []

multi_targets.append(
    {
        'targets':[
            {
                'genre': 'Electro Pop',
                'target_circumplex': [0.5, 0.3],
                'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
                'weighting': '100', 
                'avg_date': '2010-01-01',
            }
        ],
        'duration': 1800,
    }
)
multi_targets.append(
    {
        'targets': [
            {
                'genre': 'House',
                'target_circumplex': [0.5, 0.3],
                'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
                'weighting': '100', 
                'avg_date': '2022-12-12',
            },
        ],
        'duration': 1800,
    }
)
multi_targets.append(
    {
        'targets': 'fitness-pop',
        'duration': 1800,
    }
)


out = multi_target_playlist_creation(access_token, multi_targets)

import ipdb; ipdb.set_trace()