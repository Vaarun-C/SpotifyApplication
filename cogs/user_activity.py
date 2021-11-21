import discord
from discord.ext import commands, tasks

class user_activity(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		self.stalk.start()

	#Check user's activity and if they are listening to Spotify start the get_song task. Repeat every hour
	@tasks.loop(hours=1)
	async def stalk(self):
	
		online = []
	
		for person in self.client.people:
			if (str(person.status) == "offline"):
				continue
			
			for activity in person.activities:
				if(isinstance(activity, discord.activity.Spotify)):
					online.append(person)
	
		if((len(online) != 0) and (self.get_song.is_running() == False)):
			self.get_song.start(online)
	
		elif((len(online) == 0) and (self.get_song.is_running() == True)):
			self.get_song.stop()
	
	#Get the spotify track that the user is listening to and send the uri to temp channel to add to New Music. Repeat every 2 minutes
	@tasks.loop(minutes=2)
	async def get_song(self, members):
	
		already_tracked = await self.client.stalk_channel.history(limit=1).flatten()
	
		for person in members:
			for activity in person.activities:
				if(isinstance(activity, discord.activity.Spotify)):
					for song in already_tracked:
						if(song.content != ("spotify:track:" + str(activity.track_id))):
							await self.client.stalk_channel.send("spotify:track:" + str(activity.track_id))

def setup(client):
	client.add_cog(user_activity(client))