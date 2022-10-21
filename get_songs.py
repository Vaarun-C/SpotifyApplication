class get_songs(): 

	#Get list of user's liked songs
	async def getLikedSongs(self, sp, only_tracks=False, limit=True):
	
		liked = []
	
		#Get user liked songs playlist and get each track as an object
		track_objects = sp.current_user_saved_tracks()
		tracks = track_objects['items']
		hello
	
		#This is the workaraound for the 100 track get limit. It stores all the tracks in playlist as objects instead of just first 100
		while track_objects['next']:
			track_objects = sp.next(track_objects)
			tracks.extend(track_objects['items'])

		#Consider only the 50 newest tracks
		if(limit):
			tracks = tracks[:51]
	
		for song in tracks:
			liked.append(song.get('track').get('uri'))
	
		if (only_tracks == True):
			return(tracks)
	
		return (liked)

	#Get songs from Must listen and Must Listen(mine) and return their uris
	async def getPlaylistSongs(self, sp, username, my_playlist_id, collab_playlist_id):
	
		collab_must_listen_songs = []
		must_listen_songs = []
	
		#Get songs in Must Listen(mine) as objects
		track_objects = sp.user_playlist_tracks(username,my_playlist_id)
		tracks = track_objects['items']
	
		#This is the workaraound for the 100 track get limit. It stores all the tracks in playlist as objects instead of just first 100
		while track_objects['next']:
			track_objects = sp.next(track_objects)
			tracks.extend(track_objects['items'])
	
		#Get song uris
		for song in tracks:
			must_listen_songs.append(song.get('track').get('uri'))
	
		#Do the same for must listen(collaborative)
		track_objects = sp.playlist_tracks(collab_playlist_id)
		tracks = track_objects['items']
	
		while track_objects['next']:
			track_objects = sp.next(track_objects)
			tracks.extend(track_objects['items'])
	
		for song in tracks:
			collab_must_listen_songs.append(song.get('track').get('uri'))
	
		return({"collab_must_listen": collab_must_listen_songs,
				"must_listen": must_listen_songs})
	
	#Get songs in New Music and return their uris
	async def getNewMusicSongs(self, sp, new_music_playlist_id, only_tracks=False):
	
		new_music = []
	
		#Get song uris in new music playlist
		track_objects = sp.playlist_tracks(new_music_playlist_id)
		tracks = track_objects['items']
	
		#This is the workaraound for the 100 track get limit. It stores all the tracks in playlist as objects instead of just first 100
		while track_objects['next']:
			track_objects = sp.next(track_objects)
			tracks.extend(track_objects['items'])
	
		#Get song uris
		for song in tracks:
			new_music.append(song.get('track').get('uri'))
	
		if(only_tracks == True):
			return(tracks)
	
		return(new_music)