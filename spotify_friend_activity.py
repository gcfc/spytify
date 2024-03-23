import subprocess
import time
import pickle
import os
import sys
import requests
from pprint import pprint
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = 5
SP_DC = os.environ["SP_DC"]
PLAYLIST_ID = os.environ["PLAYLIST_ID"]

PICKLE_FILE = os.path.join(sys.path[0], "history.pkl")
if os.path.exists(PICKLE_FILE) and os.path.getsize(PICKLE_FILE) > 0:
    with open(PICKLE_FILE, "rb") as f:
        pickle_data = pickle.load(f)
else:
    pickle_data = dict()

def get_access_token() -> str:
    access_token_url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
    headers = {"Cookie": f"sp_dc={SP_DC}"}
    response = requests.get(url=access_token_url, headers=headers)
    if not (response.status_code == 200):
        print("Cannot request access token.")
        return None
    if not (response.json() and "accessToken" in response.json()):
        print("Cannot parse JSON for access token.")
        return None
    return response.json()["accessToken"]

def sync_playlist(access_token):
    total, offset = None, 0
    all_uris = set()
    while total is None or offset < total:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market=US&limit=100&offset={offset}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url=url, headers=headers)
        if not (response.status_code == 200):
            raise ConnectionError("Cannot sync playlist.")
        if not response.json():
            raise RuntimeError("Cannot parse playlist JSON.")
        if total is None:
            total = response.json()["total"]
        all_uris.update(set(song['track']['uri'] for song in response.json()["items"] if song['track'] is not None))
        offset += 100
    return all_uris 

def scan_activity(access_token):
    js_file = os.path.join(sys.path[0], "scan_activity.js")
    p = subprocess.Popen(['node', js_file, access_token], stdout=subprocess.PIPE)
    activity_dict = p.stdout.read().decode().strip()
    try:
        activity_dict = dict(eval(activity_dict))
        success = True
    except:
        print("Nodejs error, output cannot be converted to dictionary!")
        activity_dict = None
        success = False

    return activity_dict, success

def parse_and_pickle(activity_dict, all_uris):
    activity_uris = set()
    success = True
    if "friends" in activity_dict:
        friends = activity_dict["friends"]

        for friend in friends:
            try:
                user = friend["user"]["name"]
                song = friend["track"]["name"]
                album = friend["track"]["album"]["name"]
                artist = friend["track"]["artist"]["name"]
                playlist = friend["track"]["context"]["name"]
                uri = friend["track"]["uri"]
                activity_uris.add(uri)
                pickle_data.setdefault(user, set()).add((song, album, artist, playlist, uri))
            except Exception as e:
                success = False
                print(e)
                print("Continuing...")
                # In case only some are successful, they are still parsed. 
        
        new_uris = activity_uris.difference(all_uris)
        with open(PICKLE_FILE, "wb+") as f:
            pickle.dump(pickle_data, f)
    else:
        success = False
    
    return success, new_uris

def add_to_playlist(new_uris : set, access_token : str):
    assert len(new_uris) > 0, "Should not be using this function with no new songs to add!"
    new_uris_string = '%2C'.join([uri.replace(":", "%3A") for uri in new_uris])
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?position=0&uris={new_uris_string}"
    headers = {"Authorization": f"Bearer {access_token}", 
               "Content-Type": "application/json"}
    response = requests.post(url=url, headers=headers, data={
        "uris": [
            "string"
        ],
        "position": 0
    })
    success = (response.status_code == 200)
    if not success:
        print("Cannot add new songs to playlist.")
    return success

if __name__ == "__main__":
    retries_left = MAX_RETRIES
    access_token = get_access_token()
    all_uris = sync_playlist(access_token)
    while True:
        success, write_pickle_success, add_playlist_success = True, True, True
        try:
            print(f"{dt.now()}: Scanning activity...", end=" ")
            access_token_result = get_access_token()
            access_token = access_token_result if access_token_result is not None else access_token
            activity_dict, activity_success = scan_activity(access_token)
            if activity_success and activity_dict is not None:
                write_pickle_success, new_uris = parse_and_pickle(activity_dict, all_uris)
                if not write_pickle_success:
                    print("Dictionary format mismatch!")
                    print(activity_dict)
                if new_uris:
                    add_playlist_success = add_to_playlist(new_uris, access_token)
                all_uris.update(new_uris)
                print(f"Added {len(new_uris)} song{'s' if len(new_uris) != 1 else ''} to the playlist!")
            success = success and write_pickle_success and add_playlist_success
            if not success:
                retries_left -= 1
            else:
                retries_left = MAX_RETRIES
            if retries_left <= 0:
                raise RuntimeError("Max retries reached!")
            time.sleep(75) # Max 50 requests per hour
        except KeyboardInterrupt:
            pprint(pickle_data)
            print("Have a nice day!")
            break