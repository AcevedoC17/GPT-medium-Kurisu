# the os module helps us access environment variables
# i.e., our API keys
import os, platform
try:
    import nacl
except ImportError:
    try:
      if platform.system().lower().startswith('win'):
        os.system("pip install pynacl")
      else:
        os.system("pip3 install pynacl")
    except Exception as e:
      print("Error:", e)
      exit()

# these modules are for querying the Hugging Face model
import json
import requests

# the Discord Python API
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
import asyncio

# this is my Hugging Face profile link
API_URL = 'https://api-inference.huggingface.co/models/BlightZz/'
loop = False

class MyClient(commands.Bot):
    def __init__(self, model_name, command_prefix):
        super().__init__(command_prefix = "$")
        self.command()(self.Hello)
        self.command()(self.join)
        self.command()(self.play)
        self.command()(self.resume)
        self.command()(self.stop)
        self.command()(self.pause)
        self.command()(self.hentai)
        self.command()(self.commandlist)
        self.command()(self.skip)
        self.command()(self.leave)
        self.command()(self.display)
        self.command()(self.repeat)
        self.command()(self.makePlaylist)
        self.command()(self.addtoPlaylist)
        self.command()(self.showPlaylists)
        self.command()(self.playlist)
        self.command()(self.devDisplay)
        self.queue = []
        self.queuedict = {}
        with open("servers.json", "r") as json_file:
          self.queuedict = json.load(json_file)
        self.playlistdict = {}
        with open("playlists.json", "r") as json_file:
          self.playlistdict = json.load(json_file)
        self.api_endpoint = API_URL + model_name
        # retrieve the secret API token from the system environment
        huggingface_token = os.environ['HUGGINGFACE_TOKEN']
        # format the header in our request to Hugging Face
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }





    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret
    


    async def devDisplay(self, ctx):
      await ctx.send(self.playlistdict)


















    async def on_ready(self):
        # print out information when the bot wakes up
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(activity=discord.Game(name="$play URL, or @ me to chat!"))
        # send a request to the model without caring about the response
        # just so that the model wakes up and starts loading
        self.query({'inputs': {'text': 'Hello!'}})
        
        for guild in self.guilds:
          self.queuedict[guild.id] = []
          print(guild.id)
          print("added to dict")
        with open("servers.json", "w") as outfile:
          json.dump(self.queuedict, outfile)
          print("Saved server list as json.")
        
    


    async def makePlaylist(self, ctx, *, content):
      self.playlistdict[content] = []
    

    async def playlist(self, ctx, *, content):
      for s in self.playlistdict[content]:
        try:
          self.queuedict[ctx.guild.id].append(s)
        except:
          self.queuedict[ctx.guild.id] = [s]
      await self.play(ctx, url = self.queuedict[ctx.guild.id].pop())




    async def showPlaylists(self, ctx):
      temp = "```These are the currently available playlists and their content.\n"
      count = 1
      for key, value in self.playlistdict.items():
        temp = temp + key + ":" + "\n"
        count = 1
        for s in value:
          temp = temp + str(count) + ". " + s + "\n"
          count = count + 1
      temp  = temp + "```"
      await ctx.send(temp)






    async def addtoPlaylist(self, ctx, *, content):
      targetPlaylist = content[0:content.find(',')]
      song = content[content.find(',')+2: len(content)]
      self.playlistdict[targetPlaylist].append(song)
      with open("playlists.json", "w") as outfile:
        json.dump(self.playlistdict, outfile)
      message = "Added " + "*" + song + "*" " to playlist " + "*" + targetPlaylist + "*"
      await ctx.send(message)


    async def repeat(self, ctx):
      global loop
      loop = not loop
      if loop:
        await ctx.send("I'll loop the song.")
      else:
        await ctx.send("I'll stop looping the song")
    



    async def on_message(self, message):
        # ignore the message if it comes from the bot itself
        if message.author.id == self.user.id:
           return
         # ignore if not @
        if "fuck" in message.content:
          emoji = discord.utils.get(message.guild.emojis, name = 'KurisuPout') 
          await message.add_reaction(emoji)
        if "vamo" in message.content:
          emoji = discord.utils.get(message.guild.emojis, name = 'OKabe')
          await message.add_reaction(emoji)
        if "kurisu" in message.content:
          emoji = discord.utils.get(message.guild.emojis, name = 'KurisuCute')
          await message.add_reaction(emoji)
        if "sus" in message.content:
          emoji = discord.utils.get(message.guild.emojis, name = 'Amadeus')
          await message.add_reaction(emoji)
        if "ostia" in message.content:
          emoji = discord.utils.get(message.guild.emojis, name = 'ostia')
          await message.add_reaction(emoji)
        if not self.user.mentioned_in(message):
          await self.process_commands(message)
          return
        
        # form query payload with the content of the message
        payload = {'inputs': {'text': message.content}}

        # while the bot is waiting on a response from the model
        # set the its status as typing for user-friendliness
        async with message.channel.typing():
          response = self.query(payload)
        bot_response = response.get('generated_text', None)
        # we may get ill-formed response if the model hasn't fully loaded
        # or has timed out
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'No use talking anymore.'

        # send the model's response to the Discord channel
        await message.channel.send(bot_response)



    async def display(self, ctx):
      count = 1
      temp = "```These are the songs currently in the queue:\n"
      for s in self.queuedict[ctx.guild.id]:
        temp = temp + str(count) + ". " + s + "\n"
        count = count + 1
      temp = temp + "```"
      await ctx.send(temp)

    async def Hello(self, ctx):
      await ctx.send("Hello!")
    



    async def join(self, ctx):
      channel = ctx.message.author.voice.channel
      voice = get(self.voice_clients, guild=ctx.guild)
      if voice and voice.is_connected():
        await voice.move_to(channel)
      else:
        voice = await channel.connect()
      
    



    async def play(self, ctx,*, url):
      print("play called")
      await self.join(ctx)
      message = await ctx.send('Working on it...')
      FFMPEG_OPTIONS = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'} #youtube_dl options
      YDL_OPTIONS = {'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3', 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
      'restrictfilenames': True, 'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False, 'logtostderr': False, 'quiet': True,
      'no_warnings': True, 'default_search': 'auto', 'source_address': '0.0.0.0'}
      voice = get(self.voice_clients, guild=ctx.guild)




      #Youtube stuff
      if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            results = YoutubeSearch(url, max_results=1).to_dict()
            #print(str(results))
            url2 = results[0]['id']
            #print(url2)
            info = ydl.extract_info(url2, download=False)
            URL = info['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS, ), after= lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, url), self.loop).result())
      
        
            #Auxiliary Message Handling
            voice.is_playing()
            await message.edit(content = 'Enjoy your music!\n'+ 'https://www.youtube.com/watch?v='+url2)
            emoji = discord.utils.get(ctx.guild.emojis, name = 'KurisuThumbsUp')
            emoji2 = discord.utils.get(ctx.guild.emojis, name = 'KurisuHeart')
            await message.add_reaction(emoji)
            await message.add_reaction(emoji2)
      else:
         try:
           self.queuedict[ctx.guild.id].append(url)
         except:
          self.queuedict[ctx.guild.id] = [url]
         await ctx.message.delete()
         await ctx.send("I added your song to the queue.")





    async def play_next(self, ctx, url):
      if loop:
          await self.play(ctx = ctx, url = url)
      print("play_next called")
      if len(self.queuedict[ctx.guild.id]) >= 1:
        print("play_next if success.")
        await self.play(ctx = ctx, url = self.queuedict[ctx.guild.id].pop(0))
      else:
        print("play_next else fulfilled")
        return
    


    async def leave(self, ctx):
      await ctx.message.guild.voice_client.disconnect()
      await ctx.send("See you later.")





    
    async def skip(self, ctx):
      if len(self.queuedict[ctx.guild.id]) >= 1:
        print("skip if success.")
        voice = get(self.voice_clients, guild=ctx.guild)
        if voice.is_playing():
         voice.stop()
         await ctx.send("Skipping.")
        else:
          ctx.send("What do you want me to skip? There's nothing playing.")
      else:
        voice = get(self.voice_clients, guild=ctx.guild)
        voice.stop()
        await ctx.send("The queue is empty now.")


    


        





    async def resume(self, ctx):
      voice = get(self.voice_clients, guild=ctx.guild)
      if not voice.is_playing():
        voice.resume()
        await ctx.send('Resuming.')
# check if the bot is already playing
      else:
        await ctx.send("Resume what? The music is already playing.")
        return
    



    async def pause(self, ctx):
      voice = get(self.voice_clients, guild=ctx.guild)
      if voice.is_playing():
        voice.pause()
        await ctx.send('Paused.')
      else:
        await ctx.send("Pay attention, there's nothing playing.")
    



    async def stop(self, ctx):
      voice = get(self.voice_clients, guild=ctx.guild)
      self.queue.clear()
      if voice.is_playing():
        voice.stop()
        await ctx.send('Stopped.')
      else:
        await ctx.send("Stop what? Seriously, pay attention. There's nothing playing.")

    



    async def hentai(self, ctx):
      await ctx.channel.send(file=discord.File('Horny.gif'))
    



    async def commandlist(self, ctx):
      await ctx.channel.send('Hey! These are the commands available right now:\n $join\n$play\n$resume\n$pause\n$stop\n$hentai\n\nYou can also @ me if you want to chat!')

    

def main():
    #DialoGPT-medium-Kurisu is my model name
    client = MyClient('DialoGPT-medium-Kurisu', '$')
    client.run(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':
  main()
my_secret = os.environ['DISCORD_TOKEN']
