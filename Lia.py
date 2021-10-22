import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

client = commands.Bot(command_prefix = '>')

#Load the env file
load_dotenv('.env')

#Runs when bot is ready to execute commands
@client.event
async def on_ready():

	global new_music_playlist_id, my_playlist_id, collab_playlist_id, username, sp, output_channel, not_liked_channel

	#Initialize global variables
	new_music_playlist_id = "7rkFwRu52z4pOtQbfaBJXI"
	my_playlist_id = "4U4ahmNIHjDRvSrDCQg5ji"
	collab_playlist_id = "5FZviWMbPvn9o5ldwRKhf0"
	username = "epesp2mv3gpv0dkw7y7wkk3cf"

	#Create a spotipy user client object and get authorization
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = os.getenv('CLIENT_ID'), client_secret = os.getenv('CLIENT_SECRET'), redirect_uri = os.getenv('REDIRECT_URI'), scope = "playlist-modify-private playlist-read-collaborative user-library-read"))

	#Get output channel in discord
	for text_channel in client.guilds[0].text_channels:
		if text_channel.id == 895992652896546826:
			output_channel = text_channel
		if text_channel.id == 899976005886812170:
			not_liked_channel = text_channel

	print("Ready")

#If some songs in New Music have been in the playlist for more than a month add them to Not-Liked-Songs
async def setNotLiked():
	not_liked = []

	l = await getNotLiked()

	#Get ONLY track objects from the New Music playlist
	songs = await getNewMusicSongs(True)

	#Check if the song was added in the same year and the same month as today and whether it is already there in Not-Liked-Songs or not. If not add it to not_liked
	for song in songs:
		if(((int(song.get('added_at')[:4]) != datetime.today().year) or (int(song.get('added_at')[5:7]) != datetime.today().month)) and (song.get('track').get('uri') not in l)):
			not_liked.append(song.get('track'))

	#Send the not-liked elements in the not-liked channel
	for song in not_liked:
		await not_liked_channel.send(song.get('uri') + " " + song.get('name'))

#Read messages from the not-liked channel return the songs there in the form of a list
async def getNotLiked():
	not_liked_song_messages = await not_liked_channel.history(limit=1000).flatten()
	not_liked_songs = []

	for message in not_liked_song_messages:
		not_liked_songs.append((message.content.split(" "))[0])

	#Return not_liked_songs
	return(not_liked_songs)

#Get list of user's liked songs
async def getLikedSongs(only_tracks=False):

	liked = []

	#Get user liked songs playlist and get each track as an object
	track_objects = sp.current_user_saved_tracks()
	tracks = track_objects['items']

	#This is the workaraound for the 100 track get limit. It stores all the tracks in playlist as objects instead of just first 100
	while track_objects['next']:
		track_objects = sp.next(track_objects)
		tracks.extend(track_objects['items'])

	for song in tracks:
		liked.append(song.get('track').get('uri'))

	await output_channel.send("Got Liked Songs")

	if (only_tracks == True):
		return(tracks)

	return (liked)

#Get songs from Must listen and Must Listen(mine) and return their uris
async def getPlaylistSongs():

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

	await output_channel.send("Got songs in playlists")

	return({"collab_must_listen": collab_must_listen_songs,
			"must_listen": must_listen_songs})

#Get songs in New Music and return their uris
async def getNewMusicSongs(only_tracks=False):

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

	await output_channel.send("Got songs in New Music")

	if(only_tracks == True):
		return(tracks)

	return(new_music)

#Filter liked songs by genre
async def filterLiked(liked_songs):

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

	await output_channel.send("Filtered Liked Songs by genre")
	return(new_tracks)

#Check for new songs to add
async def checkSongs(music_uris):

	new_songs = [] 
	add_to_my_playlist = []
	add_to_collab = []

	await output_channel.send("Checking for new songs")

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

#Remove already liked songs in New Music (Cause thats the purpose of the playlist)
@client.command()
async def cleanPlaylist(ctx):
	await output_channel.send("Cleaning New Music playlist")
	songs_to_remove = []

	#Get songs that are not liked
	await setNotLiked()
	not_liked = await getNotLiked()

	#Add them to songs_to_remove so that they can be removed
	songs_to_remove.extend(not_liked)

	new_music_ids = await getNewMusicSongs() #Get songs already in New Music playlist
	liked_songs_ids = await getLikedSongs() #Get liked songs

	#Check if any songs in New Music are also there in liked, if so add them to songs_to_remove
	for song in new_music_ids:
		if(song in liked_songs_ids):
			songs_to_remove.append(song)

	#Remove the list of songs
	sp.playlist_remove_all_occurrences_of_items(new_music_playlist_id, songs_to_remove)
	await output_channel.send("Playlist cleaned")

#Add songs to must listen and my playlist
@client.command()
async def findSongs(ctx):

	await output_channel.send("Connecting to Spotify")

	#Get songs in must listen(collab) and Must Listen(mine), also get songs in New Music and Liked songs
	playlist_songs = await getPlaylistSongs()
	new_music_songs = await getNewMusicSongs()
	liked_songs = await filterLiked(await getLikedSongs(True))

	music = {'liked_songs': liked_songs,
			 'my_playlist_songs': playlist_songs.get('must_listen'),
			 'collab_playlist_songs': playlist_songs.get('collab_must_listen'),
			 'new_music_songs': new_music_songs}

	#Check songs to find new music to add
	songs_to_add = await checkSongs(music)

	#Check if no new songs are available to add and stop here if yes
	if(len(songs_to_add.get('add_to_my_playlist')) == 0 and len(songs_to_add.get('add_to_collab')) == 0 and len(songs_to_add.get('new_songs')) == 0):
		await output_channel.send("No new songs to add")
		return

	#Send the uris of new songs to be added to must listen, in the output channel so that Mozart can add them
	for song in songs_to_add.get('add_to_collab'):
		await output_channel.send("!add " + song)
		time.sleep(2)

	#Add songs to my personal playlist
	if (len(songs_to_add.get('add_to_my_playlist')) != 0):

		i = 0
		while(i+100 < len(songs_to_add.get('add_to_my_playlist'))):
			sp.playlist_add_items(my_playlist_id, songs_to_add.get('add_to_my_playlist')[i:i+100]) #Send the songs to the api call 100 at a time due to limitation
			i = i+100

		sp.playlist_add_items(my_playlist_id, songs_to_add.get('add_to_my_playlist')[i:len(songs_to_add.get('add_to_my_playlist'))]) #Send the leftover tracks

	#Add new songs to my New Songs playlist
	if (len(songs_to_add.get('new_songs')) != 0):
		
		j = 0
		while(j+100 < len(songs_to_add.get('new_songs'))):
			sp.playlist_add_items(new_music_playlist_id, songs_to_add.get('new_songs')[j:j+100]) #Send the songs to the api call 100 at a time due to limitation
			j = j+100

		sp.playlist_add_items(new_music_playlist_id, songs_to_add.get('new_songs')[j:len(songs_to_add.get('new_songs'))]) #Send the leftover tracks

	await ctx.send('Done')

	#Clean the New Music Playlist
	time.sleep(3)
	await cleanPlaylist(ctx)

	#Clear the output channel
	time.sleep(15)
	await output_channel.purge(limit=1000)
		
#Runs the bot
client.run(os.getenv('LIATOKEN'))