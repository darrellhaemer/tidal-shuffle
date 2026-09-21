# TIDAL Shuffle Scripts

Two small Python scripts that give you a **shuffle that never repeats a song** until the whole playlist has played.

TIDAL's built-in shuffle can repeat songs and clump things together. These scripts work around that: they read one of your playlists, put the tracks in a random order, and save the result as a **new playlist**. You turn TIDAL's shuffle *off* and play the new playlist from the top. Every track plays exactly once.

- **`tidal_shuffle.py`** makes a plain random shuffle, named `Your Playlist (Shuffled)`.
- **`tidal_shuffle_spaced.py`** makes a random shuffle that also keeps the same main artist from coming up again within a set number of tracks (default 5), named `Your Playlist (Spaced Shuffle)`.

**Your original playlist is never changed.** The scripts only read from it and create a new playlist.


## Please read first

- **This is unofficial.** It is not made, endorsed, or supported by TIDAL. It uses the unofficial [`tidalapi`](https://pypi.org/project/tidalapi/) library, which relies on parts of TIDAL that aren't officially documented for this use. TIDAL could change things at any time and break it. I can't guarantee it will keep working, and you use it at your own risk. Check TIDAL's terms of service if you're unsure.

## IMPORTANT - PLEASE READ
- **Never share `tidal_session.json`.** The first time you run a script, it saves a file called `tidal_session.json` next to it. That file works like a saved login to your TIDAL account. Don't upload it, email it, or include it in a zip. If it ever gets out, change your TIDAL password and sign out your other sessions.
- **Your password is never handled by the script.** You log in on TIDAL's own website by approving a link, and the script only receives the resulting login token.
- **Tested only on Windows**, with Python 3.14 and `tidalapi` version REPLACE_WITH_VERSION. Other recent versions of Python 3 will likely work, and Mac/Linux probably work too, but I haven't tested them.


## Setup

### 1. Install Python

Download Python from the official site, **https://www.python.org/downloads/**, and run the installer. Only download it from python.org.

On Windows, the installer may offer to add Python to your PATH. Say **yes** (`y`, or tick the "Add python.exe to PATH" checkbox). If it asks whether to install Python (CPython) now, say **yes**.

Then **close any open PowerShell or Terminal window and open a new one (press the Windows key, type Powershell, press Enter)**, and check that it worked by entering:
```
python --version
```

You should see a version number. If Windows says `python` isn't recognized, try `py --version`, and use `py` instead of `python` for the rest of these steps. On Mac/Linux you may need `python3` instead of `python`.


### 2. Install the TIDAL library

In Powershell, enter:
```
python -m pip install tidalapi
```

You may see warnings about scripts being installed in a location that is "not on PATH". You can ignore those.


### 3. Get the scripts

Download `tidal_shuffle.py` and `tidal_shuffle_spaced.py` and put them in a folder.

## Using it

1. You should be able to double-click either tidal_shuffle.py or tidal_shuffle_spaced.py to run it. If that works, skip down to step 2. If double-clicking doesn't work, try the following:

A. Open PowerShell (or Terminal) and navigate to your folder with something like:
   ```
   cd C:\TidalShuffle
   ```
B. Run one of the scripts by entering either of the following:
   ```
   python tidal_shuffle.py
   python tidal_shuffle_spaced.py
   ```

2. **First run only:** the script prints a link. Open it in your browser and approve the login with your TIDAL account. The script then continues on its own.
3. Type the number of the playlist you want to shuffle and press Enter.
4. Wait a few seconds. When it says it's done, find the new playlist in TIDAL.
5. In TIDAL, turn **shuffle off**, make sure the playlist is sorted by **Date Added** (that column holds the shuffled order), and press play on the first track.

Each run creates a new playlist. Delete old shuffled copies by hand when you're done with them.

TIP: Tidal may not display your new playlist in the left column. To refresh it, simply Sort the All Playlists area and your new playlist should appear.


## Settings

In `tidal_shuffle_spaced.py`, near the top of the file:

`
MIN_ARTIST_GAP = 5
`

This is the minimum number of *other* tracks between two songs by the same main artist. Only the main artist counts (featured artists are ignored). If a playlist is dominated by one artist, the gap can't always be met, and the script spaces them as far apart as it can. It prints how many tracks couldn't meet the gap before it creates the playlist.

## Troubleshooting

- **The new playlist isn't in TIDAL's left sidebar.** It shows up in your playlists list but the sidebar may not refresh until you restart the app. Re-sorting the "All Playlists" area also refreshes it.
- **Login fails or keeps failing.** Delete `tidal_session.json` from the script's folder and run again.
- **The copy has fewer tracks than the original.** Some tracks may be unavailable in your region or may have been removed from TIDAL.
- **It stopped partway through.** Delete the incomplete playlist in TIDAL and run again. Your original is unaffected.
- **It used to work and now doesn't.** TIDAL or `tidalapi` may have changed. Try `python -m pip install --upgrade tidalapi`. If that doesn't help, open an issue with the full error message.

## Disclaimer

Not affiliated with TIDAL. TIDAL is a trademark of its owner. This software is provided as is, without warranty of any kind. See the LICENSE file.
