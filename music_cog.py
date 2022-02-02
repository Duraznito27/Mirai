import discord
from discord.ext import commands
from random import choice

from youtube_dl import YoutubeDL

client = commands.Bot(command_prefix = '!')

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.client = client

        self.is_playing = False

        self.music_queue = []
        self.YDL_OPTIONS = {    
          'format': 'bestaudio/best',
          'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
          'restrictfilenames': True,
          'noplaylist': True,
          'nocheckcertificate': True,
          'ignoreerrors': False,
          'logtostderr': False,
          'quiet': True,
          'no_warnings': True
        }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = ""

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                self.info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {
          'source': self.info['formats'][0]['url'], 
          'youtube_url' : self.info['webpage_url'],
          'title': self.info['title'],
          'channel': self.info['channel'],
          'channel_url': self.info['channel_url'],
          'thumbnail': self.info['thumbnail'],
          'duration': self.info['duration']

          }
        
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @client.command()
    async def p(self, ctx, *args):

      query = " ".join(args)
      song = self.search_yt(query)
      member = ctx.message.author
      avatar = member.avatar_url
      
      namae = song['title']
      chaneru = song['channel']
      iuarel = song['youtube_url']

      #embed 1
      added = discord.Embed(
        title = namae,
        description = chaneru,
        url = iuarel,
        color = 0x52cbff
      )
      
      added.set_image(url = song['thumbnail'])
      added.set_footer(text = f'Pedida por: {ctx.author}')

      #embed 2
      queue = discord.Embed(
        title = namae,
        description = chaneru,
        url = iuarel,
        color = 0x52cbff
      )

      queue.add_field(name = 'ㅤ', value = 'Ha sido añadida a la lista de reproducción', inline = False)
      queue.set_author(name = 'Lista de reproducción 📋', icon_url = avatar)
      queue.set_footer(text = f'Pedida por: {ctx.author}')
  
      #embed 3
      playing = discord.Embed(
        title = namae,
        description = chaneru,
        url = iuarel,
        color = 0x52cbff
      )

      playing.set_author(name = 'Reproduciendo 🎵')
      playing.set_footer(text = f'Pedida por: {ctx.author}')

      voice_channel = ctx.author.voice.channel
      if voice_channel is None:
            await ctx.send("Antes debes meterte a un canal de voz")
      else:
            if type(song) == type(True):
                await ctx.send("Hubo un error al intentar reproducir la canción >-<")
            else:
                await ctx.send(embed=added)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == True:
                  await ctx.send(embed=queue)

                else:
                  await self.play_music()
                  await ctx.send(embed=playing)
 

    @client.command()
    async def q(self, ctx):

        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"

        embed = discord.Embed(
        title = "Lista de reproducción",
        description = (retval),
        color = 0x52cbff
        )

        print(retval)

        if retval != "":
            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay musica en la lista :(")

    @client.command()
    async def skip(self, ctx):
        if self.is_playing == True:
            self.vc.stop()

            await self.play_music()
            await ctx.send("Canción saltada")
        else:
          await ctx.send("Wtf no estoy reproduciendo nada xD")
            
    @client.command()
    async def fuckoff(self, ctx):
        await self.vc.disconnect()
        await ctx.send("Desconectada 😵")
      
    @client.command()
    async def pause(self, ctx):
        await ctx.send("Pausada ⏸")
        await self.vc.pause()


    @client.command()
    async def resume(self, ctx):
        await ctx.send("Resumiendo ▶")
        await self.vc.resume()

    @client.command()
    async def np(self, ctx):
        await ctx.send('no funciona xd')
