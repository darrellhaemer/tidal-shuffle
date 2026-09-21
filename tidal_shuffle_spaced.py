"""
TIDAL Spaced Shuffle
--------------------
Makes a shuffled COPY of one of your TIDAL playlists, arranged so the same
main artist doesn't come up again within MIN_ARTIST_GAP tracks (when possible).
The original playlist is never changed.

Uses the unofficial 'tidalapi' library:  pip install tidalapi
"""

import random
from pathlib import Path

import tidalapi

# ---- Settings you can edit ---------------------------------------------------
# Minimum number of OTHER tracks between two songs by the same main artist.
# 5 means: after an artist plays, at least 5 different tracks play before
# that artist can come up again.
MIN_ARTIST_GAP = 5
# -----------------------------------------------------------------------------

# Your login is saved here after the first run, so you only approve it once.
# (If this file is in the same folder as the simple version, they share it.)
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


def artist_key(track):
    """Identify a track's MAIN artist. Tracks with no artist info get a unique
    key, so they are never treated as 'the same artist' as anything else."""
    artist = getattr(track, "artist", None)
    artist_id = getattr(artist, "id", None)
    if artist_id is None:
        return ("no-artist", track.id)
    return artist_id


def spaced_shuffle(tracks, gap):
    """
    Return the tracks in a random order where the same main artist is kept at
    least `gap` tracks apart whenever that is possible.

    How it works, one slot at a time:
      1. Only artists who haven't played in the last `gap` tracks are eligible.
      2. Normally, pick an eligible artist at random, weighted by how many of
         their tracks are still waiting. (That is the same as picking a random
         remaining track, so the result stays truly random.)
      3. But if an artist has so many tracks left that they'd no longer fit
         at the required spacing, they jump the queue. This stops big artists'
         tracks from piling up at the end of the list.
      4. If nobody is eligible, relax the rule: pick the artist who played
         longest ago.
    """
    tracks = list(tracks)
    random.shuffle(tracks)  # random order within each artist

    # Group tracks by main artist.
    groups = {}
    for t in tracks:
        groups.setdefault(artist_key(t), []).append(t)

    result = []
    recent = []  # artist keys of the last `gap` tracks, oldest first
    total = len(tracks)

    def slots_needed(key):
        # Fewest slots this artist's remaining tracks could possibly fit in.
        return (len(groups[key]) - 1) * (gap + 1) + 1

    while len(result) < total:
        slots_left = total - len(result)
        available = [k for k, g in groups.items() if g]
        eligible = [k for k in available if k not in recent]

        if not eligible:
            # Rule can't be met right now: take whoever played longest ago.
            chosen = min(available, key=lambda k: recent.index(k))
        else:
            urgent = [k for k in eligible if slots_needed(k) >= slots_left]
            if urgent:
                chosen = max(urgent, key=slots_needed)
            else:
                weights = [len(groups[k]) for k in eligible]
                chosen = random.choices(eligible, weights=weights)[0]

        result.append(groups[chosen].pop())
        recent.append(chosen)
        if len(recent) > gap:
            recent.pop(0)

    return result


def count_spacing_problems(tracks, gap):
    """Count tracks that come too soon after another track by the same artist."""
    problems = 0
    for i, t in enumerate(tracks):
        key = artist_key(t)
        earlier = tracks[max(0, i - gap):i]
        if any(artist_key(e) == key for e in earlier):
            problems += 1
    return problems


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

    print(f"Shuffling with a minimum artist gap of {MIN_ARTIST_GAP}...")
    shuffled = spaced_shuffle(tracks, MIN_ARTIST_GAP)
    problems = count_spacing_problems(shuffled, MIN_ARTIST_GAP)
    print(f"Tracks that couldn't meet the artist gap: {problems} of {len(shuffled)}")

    track_ids = [t.id for t in shuffled]

    new_name = f"{source.name} (Spaced Shuffle)"
    print(f"Creating '{new_name}' with {len(track_ids)} tracks...")
    new_playlist = session.user.create_playlist(
        new_name, "Spaced shuffle made by tidal_shuffle_spaced.py"
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