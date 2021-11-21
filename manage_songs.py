import discord
from discord.ext import commands

from datetime import datetime
from get_songs import get_songs

class manage_songs():

	def __init__(self):
		self.getsongs = get_songs()

	#If some songs in New Music have been in the playlist for more than a month add them to Not-Liked-Songs
	async def setNotLiked(self, client):
		not_liked = []
	
		l = await self.getNotLiked(client)
	
		#Get ONLY track objects from the New Music playlist
		songs = await self.getsongs.getNewMusicSongs(client.sp, client.new_music_playlist_id, True)
	
		#Check if the song was added in the same year and the same month as today and whether it is already there in Not-Liked-Songs or not. If not add it to not_liked
		for song in songs:
			if(((int(song.get('added_at')[:4]) != datetime.today().year) or (int(song.get('added_at')[5:7]) != datetime.today().month)) and (song.get('track').get('uri') not in l)):
				not_liked.append(song.get('track'))
	
		#Send the not-liked elements in the not-liked channel
		for song in not_liked:
			await client.not_liked_channel.send(song.get('uri') + " " + song.get('name'))
	
	#Read messages from the not-liked channel return the songs there in the form of a list
	async def getNotLiked(self, client):
		not_liked_song_messages = await client.not_liked_channel.history(limit=1000).flatten()
		not_liked_songs = []
	
		for message in not_liked_song_messages:
			not_liked_songs.append((message.content.split(" "))[0])
	
		#Return not_liked_songs
		return(not_liked_songs)
	
	#Filter liked songs by genre
	async def filterLiked(self, sp, liked_songs):
	
		new_tracks = []
	
		#Get all the genres that the artists have produced tracks in (because spotify doesn't provide genre for each seperate track), and remove asmr and dubstep
		for song in liked_songs:
	
			artists = []
			genres = []
	
			#Get genres
			j=0
			while j < len(song.get('track').get('artists')):
				artist = sp.artist(song.get('track').get('artists')[j].get('external_urls').get('spotify'))
				genres.extend(artist.get('genres'))
				j = j+1
	
			#Check names of artists as well (Cause I'm paranoid)
			i=0
			while i < len(song.get('track').get('artists')):
				artists.append(song.get('track').get('artists')[i].get('name'))
				i = i+1
	
			if(('asmr' in genres) or ('dubstep' in genres) or ('deathstep' in genres) or ('gaming dubstep' in genres) or ('Gibi ASMR' in artists) or ('Jojo\'s ASMR' in artists)):
				continue
	
			#Add all the other tracks to new_tracks
			new_tracks.append(song.get('track').get('uri'))
	
		return(new_tracks)

	#Check for new songs to add
	async def checkSongs(self, music_uris):
	
		new_songs = [] 
		add_to_my_playlist = []
		add_to_collab = []
	
		#Check if there is any new songs in must listen or Must Listen(mine), if so add them to new_songs
		for song in music_uris.get('my_playlist_songs'):
			if((song not in music_uris.get('liked_songs')) and (song not in music_uris.get('new_music_songs'))):
				new_songs.append(song)
	
		for song in music_uris.get('collab_playlist_songs'):
			if((song not in music_uris.get('liked_songs')) and (song not in music_uris.get('new_music_songs'))):
				new_songs.append(song)
	
		#Check for duplicates and add new songs to add to two new lists one for my personal playlist and the other for must listen
		for liked in music_uris.get('liked_songs'):
	
			if(liked not in music_uris.get('my_playlist_songs')):
				add_to_my_playlist.append(liked)
	
			if(liked not in music_uris.get('collab_playlist_songs')):
				add_to_collab.append(liked)
	
		#Return the list of new music to add to respective playlists
		return({"new_songs": new_songs,
				"add_to_my_playlist": add_to_my_playlist,
				"add_to_collab": add_to_collab})	