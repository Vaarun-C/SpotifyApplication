import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from get_songs import get_songs
from manage_songs import manage_songs

class clean_playlist(commands.Cog):

	server_ids = [836276013830635590]

	def __init__(self, client):
		self.client = client
		self.getsongs = get_songs()
		self.managesongs = manage_songs()
	
	#Remove already liked songs in New Music (Cause thats the purpose of the playlist)
	@cog_ext.cog_slash(	name="cleanPlaylist",
						description="Remove already liked songs in New Music",
						guild_ids=server_ids
	)

	async def cleanPlaylist(self, ctx):
		await ctx.send("Cleaning New Music playlist")
		songs_to_remove = []
	
		#Get songs that are not liked
		await self.managesongs.setNotLiked(self.client)
		not_liked = await self.managesongs.getNotLiked(self.client)
	
		#Add them to songs_to_remove so that they can be removed
		songs_to_remove.extend(not_liked)
	
		new_music_ids = await self.getsongs.getNewMusicSongs(self.client.sp, self.client.new_music_playlist_id) #Get songs already in New Music playlist
		liked_songs_ids = await self.getsongs.getLikedSongs(self.client.sp, limit=False) #Get liked songs
	
		#Check if any songs in New Music are also there in liked, if so add them to songs_to_remove
		for song in new_music_ids:
			if(song in liked_songs_ids):
				songs_to_remove.append(song)
	
		#Remove the list of songs
		i = 0
		while(i+100 < len(songs_to_remove)):
			self.client.sp.playlist_remove_all_occurrences_of_items(self.client.new_music_playlist_id, songs_to_remove[i:i+100]) #Send the songs to the api call 100 at a time due to limitation
			i = i+100
	
		self.client.sp.playlist_remove_all_occurrences_of_items(self.client.new_music_playlist_id, songs_to_remove[i:len(songs_to_remove)]) #Send the leftover tracks
		await ctx.send("Playlist cleaned")

	@cog_ext.cog_slash(	name="remove_not_liked",
						description="Remove stored not liked songs",
						guild_ids=server_ids
	)
	async def remove_not_liked(self, ctx):
		await self.client.not_liked_channel.purge(limit=1000)
		await ctx.send("Done")

def setup(client):
	client.add_cog(clean_playlist(client))