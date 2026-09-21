"""
TIDAL Shuffle
-------------
Makes a randomly shuffled COPY of one of your TIDAL playlists.
The original playlist is never changed.

Uses the unofficial 'tidalapi' library:  pip install tidalapi
"""

import random
from pathlib import Path

import tidalapi

# Your login is saved here after the first run, so you only approve it once.
SESSION_FILE = Path(__file__).parent / "tidal_session.json"

# TIDAL handles playlist tracks in chunks of about 100.
CHUNK = 100


def log_in():
    session = tidalapi.Session()
    # First run: prints a link. Open it in your browser and approve the login.
    # Later runs: reuses the saved login automatically.
    session.login_session_file(SESSION_FILE)
    if not session.check_login():
        raise SystemExit(
            "Login failed. Delete tidal_session.json (if it exists) and try again."
        )
    return session


def get_all_tracks(playlist):
    """Read every track from the playlist, one chunk at a time."""
    tracks = []
    total = playlist.num_tracks
    while len(tracks) < total:
        batch = playlist.tracks(limit=CHUNK, offset=len(tracks))
        if not batch:
            break
        tracks.extend(batch)
    if len(tracks) != total:
        print(f"Note: TIDAL reports {total} items but {len(tracks)} tracks were read.")
    return tracks


def choose_playlist(playlists):
    print("\nYour playlists:\n")
    for i, p in enumerate(playlists, start=1):
        print(f"  {i:>3}.  {p.name}  ({p.num_tracks} tracks)")
    while True:
        answer = input("\nType the number of the playlist to shuffle: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(playlists):
            return playlists[int(answer) - 1]
        print("That isn't a valid number, try again.")


def main():
    session = log_in()
    print("Logged in.")

    playlists = session.user.playlists()
    if not playlists:
        raise SystemExit("No playlists found on this account.")

    source = choose_playlist(playlists)
    print(f"\nReading '{source.name}'...")
    tracks = get_all_tracks(source)
    if not tracks:
        raise SystemExit("That playlist has no tracks to shuffle.")

    random.shuffle(tracks)  # a true shuffle: every track appears exactly once
    track_ids = [t.id for t in tracks]

    new_name = f"{source.name} (Shuffled)"
    print(f"Creating '{new_name}' with {len(track_ids)} tracks...")
    new_playlist = session.user.create_playlist(
        new_name, "Shuffled copy made by tidal_shuffle.py"
    )

    added = 0
    for start in range(0, len(track_ids), CHUNK):
        chunk = track_ids[start:start + CHUNK]
        new_playlist.add(chunk, allow_duplicates=True)
        added += len(chunk)
        print(f"  added {added} / {len(track_ids)}")

    print(f"\nDone! Look for '{new_name}' in your TIDAL playlists.")
    print("Turn shuffle OFF in TIDAL and play it from the top.")


if __name__ == "__main__":
    main()