# Spytify

_Infuse your Spotify playlist with the latest tracks your friends are jamming to._


## Setup and Build

This package uses [Python](https://www.python.org/downloads/) and [Nodejs](https://nodejs.org/en). Follow the links to download and install them if you haven't. 

Clone this repository, or you can [download](https://github.com/gcfc/spytify/archive/refs/heads/main.zip) and extract it. 

In a terminal, navigate to this `spytify` directory and run 

```bash
npm install
```

and 

```bash
python -m pip install -r requirements.txt
```

This will install the necessary Javascript and Python dependencies for this package.  


### Environment Variables

In this `spytify` directory, create a file called `.env` with these lines:

```
SP_DC="..."
PLAYLIST_ID="..."
```

Let's find these two values (to replace the `"..."`) in the following sections. 

#### `sp_dc` Cookie From Spotify

1. Log into the [Spotify web player](https://open.spotify.com/)
2. Press `Cmd+Option+I` (Mac) or `Ctrl+Shift+I` (Windows) or `F12`. This should open the developer tools in your browser.
3. Go into the `Application` tab.
4. In the left section go into `Storage > Cookies > open.spotify.com`
5. Find the `sp_dc` on the right and copy its value. It should be a long string. 
6. This is the first value needed in the `.env` file. Paste it in and keep the quotes.
7. Close the window (without logging out).

Note that the `sp_dc` cookie is valid for a year or so. 

#### Playlist ID

Choose an existing Spotify playlist you want to add songs to or create a new one. To find its ID, share the playlist from Spotify as a link. It should look something like this: https://open.spotify.com/playlist/24J4jmPZMVfpDgj9xHfYbo?si=57540f0511824bac

Starting from the `/` after `playlist` to the first `?` you see (if there are any), this is the playlist ID. In this case, `24J4jmPZMVfpDgj9xHfYbo`. 

This is the second value needed in the `.env` file. Paste it in and keep the quotes.

### Finally, Run It

Still in the terminal in the `spytify` directory, run this in the terminal 

```bash
python spotify_friend_activity.py
```
And leave it running for as long as you'd like. You should see new songs being added to the playlist of your choice automatically. 