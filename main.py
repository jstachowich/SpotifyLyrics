
from functions import *




test = get_playlist_tracks("https://open.spotify.com/playlist/3dEbinUbpQmbnkfHGnn1x0?si=16369980c64e4a85")


test2 = lyrics_onto_playlist(test)

test3 = parse_for_words(test2, ['heart'])
