import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
import time
from get_songs import get_songs
from manage_songs import manage_songs

intents = discord.Intents.all()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix = '>', intents=intents)
slash = SlashCommand(client, sync_commands=True)

#Runs when bot is ready to execute commands
@client.event
async def on_ready():

	#Initialize global variables
	client.new_music_playlist_id = "7rkFwRu52z4pOtQbfaBJXI"
	client.my_playlist_id = "4U4ahmNIHjDRvSrDCQg5ji"
	client.collab_playlist_id = "5FZviWMbPvn9o5ldwRKhf0"
	client.username = "epesp2mv3gpv0dkw7y7wkk3cf"

	client.getsongs = get_songs()
	client.managesongs = manage_songs()

	#Users to stalk
	client.people =[
		client.guilds[0].get_member(730028657581490176), #Ganther
		client.guilds[0].get_member(896052473494650940)  #Moto
	]

	#Create a spotipy user client object and get authorization
	client.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = os.environ['CLIENT_ID'], client_secret = os.environ['CLIENT_SECRET'], redirect_uri = os.environ['REDIRECT_URI'], scope = "playlist-modify-private playlist-read-collaborative user-library-read"))

	#Get output channel in discord
	for text_channel in client.guilds[0].text_channels:
		if text_channel.id == 895992652896546826:
			client.output_channel = text_channel
		if text_channel.id == 899976005886812170:
			client.not_liked_channel = text_channel
		if text_channel.id == 904763605008920626:
			client.stalk_channel = text_channel

	print("Ready")

#Add songs to must listen and my playlist
@slash.slash(
	name="findSongs",
	description="Searches for new songs and adds them to respective playlists",
	guild_ids=[836276013830635590]
)

async def findSongs(ctx):

	await ctx.send("Connecting to Spotify")

	#Get songs in must listen(collab) and Must Listen(mine), also get songs in New Music and Liked songs
	playlist_songs = await client.getsongs.getPlaylistSongs(client.sp, client.username, client.my_playlist_id, client.collab_playlist_id)
	await ctx.send("Got songs in playlists")

	new_music_songs = await client.getsongs.getNewMusicSongs(client.sp, client.new_music_playlist_id)
	await ctx.send("Got songs in New Music")

	liked_songs = await client.managesongs.filterLiked(client.sp, (await client.getsongs.getLikedSongs(client.sp, True)))
	await ctx.send("Got liked songs")

	#Get the songs from stalk_channel and add them as well
	stalk_music = await client.stalk_channel.history(limit=1000).flatten()

	if(len(stalk_music) != 0):
		for song in stalk_music:
			playlist_songs["collab_must_listen"].append(song.content)

		await client.stalk_channel.purge(limit=1000)

	music = {
		'liked_songs': liked_songs,
		'my_playlist_songs': playlist_songs.get('must_listen'),
		'collab_playlist_songs': playlist_songs.get('collab_must_listen'),
		'new_music_songs': new_music_songs
	}

	#Check songs to find new music to add
	songs_to_add = await client.managesongs.checkSongs(music)

	#Check if no new songs are available to add and stop here if yes
	if(len(songs_to_add.get('add_to_my_playlist')) == 0 and len(songs_to_add.get('add_to_collab')) == 0 and len(songs_to_add.get('new_songs')) == 0):
		await client.output_channel.send("No new songs to add")
		return

	#Send the uris of new songs to be added to must listen, in the output channel so that Mozart can add them
	for song in songs_to_add.get('add_to_collab'):
		await client.output_channel.send("!add " + song)
		time.sleep(1)

	#Add songs to my personal playlist
	if (len(songs_to_add.get('add_to_my_playlist')) != 0):
		add_songs(client.my_playlist_id, songs_to_add.get("add_to_my_playlist"))

	#Add new songs to my New Songs playlist
	if (len(songs_to_add.get('new_songs')) != 0):		
		add_songs(client.new_music_playlist_id, songs_to_add.get("new_songs"))

	await ctx.send('Done')

	#Clear the output channel
	time.sleep(15)
	await client.output_channel.purge(limit=1000)

#Add songs to a playlist
async def add_songs(playlist_id, songs):

	i = 0
	while(i+100 < len(songs)):
		client.sp.playlist_add_items(playlist_id, songs[i:i+100])
		i += 100
	client.sp.playlist_add_items(playlist_id, songs[i:len(songs)])

#Load all cogs in cogs folder
for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		client.load_extension(f"cogs.{filename[:-3]}")

#Runs the bot
client.run(os.environ['TOKEN'])