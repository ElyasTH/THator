import discord
import os
import random
import requests
import customPafy
import string
import youtube_dl
import asyncio
import urllib.request
import re
import lyricsgenius
from hangman_words import words
from textblob import TextBlob
from replit import db
from keep_online import keep_alive
from bs4 import BeautifulSoup as bs
from discord.ext import commands

client = commands.Bot(command_prefix="-", case_insensitive=True, intents = discord.Intents.all(), help_command = None)
genius = lyricsgenius.Genius('8g6Noz7rPLHnKEzWfu3kCfUVMrVEJzYSpmMB9mIJ295_KVmYzTheZr_oXqTLfEdf')
limit = False
for x in db.keys():
  if "songs" in db[x].keys():
    db[x].pop('songs')

def update_words(new_word, word_value, sv_id):
  d = {new_word: word_value}
  if sv_id in db.keys():
    if "words" in db[sv_id].keys():
      db[sv_id]["words"].update(d)
    else:
      db[sv_id]["words"] = d
  else:
    db[sv_id] = {"words": d}

async def game_timer(sv_id):
  while db[sv_id]['games']['timer'] > 0:
    await asyncio.sleep(1)
    db[sv_id]['games']['timer'] -= 1
  db[sv_id]['games']['currentGame'] = 'None'



@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")
  for sv_id in db:
    if 'games' in db[sv_id]:
      db[sv_id]['games']['currentGame'] = 'None'
    else:
      db[sv_id]['games'] = {'currentGame': 'None'}


@client.event
async def on_message(message):
  global limit
  msg = message.content
  sv_id = str(message.guild.id)
  sender = str(message.author)
  
  if sender == str(client.user) or str(sender) == 'Groovy#7254':
   return

  elif msg.startswith('-add'):
    if msg.count('\'') == 4:
      new_word = msg.split("'", 2)[1]
      word_value = msg.split("'", 2)[2].replace(" '", "").replace("'", "")
      sv_id = str(message.guild.id)
      update_words(new_word, word_value, sv_id)
      await message.reply("کلمه جدید اضافه شد.")
    else:
      await message.reply("اشتباهه داش اینطوری بزن: \n-add \'filter\' \'reply\'")
  
  elif msg.startswith('-list'):
    if sv_id in db.keys() and "words" in db[sv_id].keys() and db[sv_id]["words"]:
      output = ""
      for key in db[sv_id]["words"]:
        try:
          if str(TextBlob(key).detect_language()) == "en":
            list = str(key) + " ➡ " + str(db[sv_id]["words"][key])
            output += list + "\n"
          else:
            list = str(key) + " ⬅ " + str(db[sv_id]["words"][key])
            output += list + "\n"
        except:
          list = str(key) + " : " + str(db[sv_id]["words"][key])
          output += list + "\n"
      await message.reply(output)
    else:
      await message.reply("هیچ کلمه ای یافت نشد.")

  elif msg.startswith('-del'):
    del_word = msg.split('-del ',1)[1]
    if del_word in db[sv_id]["words"] and sv_id in db.keys() and "words" in db[sv_id].keys() and db[sv_id]["words"]:
      db[sv_id]["words"].pop(del_word)
      await message.reply("\'" + del_word + "\' از لیست کلمات پاک شد." )
    else:
      await message.reply('این کلمه توی لیست نیست.')


  elif db[sv_id]['games']['currentGame'] == 'guess' and db[sv_id]['games']['player'] == sender:
    db[sv_id]['games']['timer'] = 30
    try:
      guess = int(msg)
      score = db[sv_id]['games']['guess']['current_score']
      player = db[sv_id]['games']['player']
      if guess > db[sv_id]['games']['guess']['secret_num']:
        score += 1
        db[sv_id]['games']['guess']['current_score'] = score
        await message.reply("یه عدد کوچیکتر بگو")
      elif guess < db[sv_id]['games']['guess']['secret_num']:
        score += 1
        db[sv_id]['games']['guess']['current_score'] = score
        await message.reply("یه عدد بزرگتر بگو")
      elif guess == db[sv_id]['games']['guess']['secret_num']:
        score += 1
        db[sv_id]['games']['guess']['current_score'] = score
        if 'guess' in db[sv_id]['games']:
          if 'scores' in db[sv_id]['games']['guess']:
            if player in db[sv_id]['games']['guess']['scores']:
              highscore = db[sv_id]['games']['guess']['scores'][player]
              if score < highscore:
                db[sv_id]['games']['guess']['scores'][player] = score
            else:
              db[sv_id]['games']['guess']['scores'][player] = score
          else:
            db[sv_id]['games']['guess']['scores'] = {player: score}
        else:
          db[sv_id]['games']['guess'] = {'scores': {player: score}}
        highscore = db[sv_id]['games']['guess']['scores'][player]
        await message.reply("آفرین داش درست گفتی\n" + "تعداد حدس ها: " + str(score) + "\n کمترین تعداد حدس: " + str(highscore))
        db[sv_id]['games']['currentGame'] = 'None'
    except ValueError:
      await message.reply('نخوندم')
  elif db[sv_id]['games']['currentGame'] == 'hangman' and db[sv_id]['games']['player'] == sender and msg.upper() in string.ascii_uppercase and len(msg) == 1 and not limit:
    limit = True
    db[sv_id]['games']['timer'] = 180
    word = db[sv_id]['games']['hangman']['secret_word']
    if len(db[sv_id]['games']['hangman']['remain_letters']) > 0:
      user_letter = str(msg).upper()
      if user_letter in string.ascii_uppercase and len(user_letter) == 1:
        if user_letter in db[sv_id]['games']['hangman']['used_letters']:
          await message.reply('قبلا این حرفو گفتی داش')
        elif user_letter in db[sv_id]['games']['hangman']['remain_letters']:
          db[sv_id]['games']['hangman']['used_letters'] += user_letter + ' '
          for x in db[sv_id]['games']['hangman']['remain_letters']:
            if x == user_letter:
              new = db[sv_id]['games']['hangman']['remain_letters'].replace(x, '')
              db[sv_id]['games']['hangman']['remain_letters'] = new
        else:
          db[sv_id]['games']['hangman']['used_letters'] += user_letter + ' '
          db[sv_id]['games']['hangman']['errors'] += 1
      dis_word = [letter if letter in db[sv_id]['games']['hangman']['used_letters'] else '-' for letter in word]
      errors = db[sv_id]['games']['hangman']['errors']
      used_letters = db[sv_id]['games']['hangman']['used_letters']
      embed = discord.Embed(title=' '.join(dis_word), description='حروف استفاده شده: '+ used_letters, color=0xf2ff00)
      if errors == 0:
        url= 'https://i.imgur.com/epiR9LC.png'
      elif errors == 1:
        url= 'https://i.imgur.com/qSNDz9F.png'
      elif errors == 2:
        url= 'https://i.imgur.com/KrVTFhe.png'
      elif errors == 3:
        url= 'https://i.imgur.com/2lNun6o.png'
      elif errors == 4:
        url= 'https://i.imgur.com/B5a8H1a.png'
      elif errors == 5:
        url= 'https://i.imgur.com/DWmPa2A.png'
      elif errors == 6:
        url= 'https://i.imgur.com/2teSHrf.png'
      embed.set_thumbnail(url=url)
      await message.reply(embed=embed, mention_author=False)
      
      if len(db[sv_id]['games']['hangman']['remain_letters']) == 0:
        score = db[sv_id]['games']['hangman']['letter_count']*10
        player = db[sv_id]['games']['player']
        db[sv_id]['games']['hangman']['scores'][player] += score
        db[sv_id]['games']['currentGame'] = 'None'
        highscore = db[sv_id]['games']['hangman']['scores'][player]
        await message.reply(f'آفرین داش درست گفتی\nامتیاز: {highscore}')
      elif db[sv_id]['games']['hangman']['errors'] == 6:
        score = db[sv_id]['games']['hangman']['letter_count']*10
        player = db[sv_id]['games']['player']
        highscore = db[sv_id]['games']['hangman']['scores'][player]
        db[sv_id]['games']['currentGame'] = 'None'
        await message.reply(f'باختی داش. کلمه {word} بود.\nامتیاز: {highscore}')
      await asyncio.sleep(0.5)
      limit = False

    
  elif msg.startswith('-randomgame'):
    r = requests.get('http://store.steampowered.com/explore/random/')
    soup = bs(r.content, 'html.parser')
    gameurl = str(soup.find('meta', {'property': 'og:url'})['content'])
    await message.reply(gameurl)
    

  else:
    if sv_id in db.keys() and "words" in db[sv_id].keys() and db[sv_id]["words"]:
      for key in db[sv_id]["words"]:
        if key in msg:
          await message.reply(db[sv_id]["words"][key])
  await client.process_commands(message)




@client.command(aliases=['q'])
async def queue(ctx, n1, n2='', n3='', n4='', n5='', n6='', n7='', n8='', n9='', n10=''):
  try:
    name = ' '.join(str(n1+' '+n2+' '+n3+' '+n4+' '+n5+' '+n6+' '+n7+' '+n8+' '+n9+' '+n10).split())
    sv_id = str(ctx.guild.id)
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + name.replace(" ", "+") + "+music") 
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    url = f"https://www.youtube.com/watch?v={video_ids[0]}"
    video = customPafy.new(url)
    title = video.title
    title2 = ""
    p = 0
    for i in title:
      if i == "(" or i =="[":
        p += 1
      elif i == ")" or i =="]":
        p -= 1
      elif p == 0:
        title2 += i
    if sv_id in db.keys():
      if "songs" in db[sv_id].keys():
        if title2 not in db[sv_id]["songs"]:
          db[sv_id]["songs"].append(name)
        else:
          await ctx.reply("این آهنگ از قبل توی لیست بود.")
          return
      else:
        db[sv_id]["songs"] = [name]
    else:
      db[sv_id] = {"songs": [name]}
    embed = discord.Embed(color=0x65c400 )
    embed.description = f"**آهنگ [{title2}]({url}) به لیست اضافه شد.**"
    await ctx.reply(embed=embed)
    print(db[sv_id]["songs"])
  except Exception as e:
    print(e.message)



async def play_music(ctx, time=0):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  try:
    while len(db[sv_id]["songs"]) >= 1:
      for s in db[sv_id]["songs"]:
        if sv_id in db.keys() and "songs" in db[sv_id].keys() and len(db[sv_id]["songs"]) >= 1:
          html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + s.replace(" ", "+") + "+music")
          video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
          url1 = f"https://www.youtube.com/watch?v={video_ids[0]}"
          video = customPafy.new(url1)
          if 'isgo' in db[sv_id] and db[sv_id]['isgo'] == 'no':
            t = 0
          else:
            t = time
          length = video.length
          html2 = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + s.replace(" ", "+") + "+music")
          video_ids = re.findall(r"watch\?v=(\S{11})", html2.read().decode())
          url2 = f"https://www.youtube.com/watch?v={video_ids[0]}"
          video = customPafy.new(url2)
          title = video.title
          title2 = ""
          thumb = video.thumb
          p = 0
          for i in title:
            if i == "(" or i =="[":
              p += 1
            elif i == ")" or i =="]":
              p -= 1
            elif p == 0:
              title2 += i
          
          YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist':'True',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
              }],
              }
          
          FFMPEG_OPTIONS = {
              'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': f'-vn -ss {t}'
              }

          with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url1, download=False)
            I_URL = info['formats'][0]['url']
            voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(I_URL, **FFMPEG_OPTIONS)))
            if 'volume' in db[sv_id]:
              voice.source.volume = db[sv_id]['volume']
          embed = discord.Embed(title=title2, url=url2, color=0xf2ff00)
          embed.set_thumbnail(url=thumb)
          msg = await ctx.send(embed=embed)
          n = 0
          db[sv_id]['isgo'] = 'no'
          while s in db[sv_id]["songs"] and t <= length and db[sv_id]['isgo'] == 'no': 
            embed.remove_field(index=0)
            mins, secs= divmod(t, 60)
            min2, sec2 = divmod(length, 60)
            timer = f'{mins:02d}:{secs:02d} / {min2:02d}:{sec2:02d}'
            embed.add_field(name=timer, value='\u200b')
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
            n += 1
            if n == 9:
              t += 2
              n = 0
            else:
              t += 1
          if s in db[sv_id]["songs"] and db[sv_id]['isgo'] == 'no':
            db[sv_id]["songs"].remove(s)
          await msg.delete()
    if db[sv_id]['isgo'] == 'no':
      voice.stop()
      await voice.disconnect()
    
  except Exception as e:
    print(e)
    return




@client.command(aliases=['p'])
async def play(ctx):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  try:
    if voice == None and len(db[sv_id]["songs"]) >= 1 and 'songs' in db[sv_id]:
      voiceChannel = ctx.message.author.voice.channel
      await voiceChannel.connect()
      await ctx.send("کمی صبر بنمایید...")
      await play_music(ctx)
    elif voice == None and len(db[sv_id]["songs"]) == 0:
      await ctx.reply("لیست آهنگ خالیه.")
    else:
      await ctx.reply("هم اکنون در حال پخش می باشم.")
  except AttributeError:
    await ctx.reply("اول برو توی ویس چنل.")
  except KeyError:
    await ctx.reply("لیست آهنگ خالیه.")
  


@client.command()
async def stop(ctx):
  sv_id = str(ctx.guild.id)
  try:
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await voice.disconnect()
    await ctx.reply("شو بخیر")
    for s in db[sv_id]["songs"]:
      db[sv_id]["songs"].remove(s)
  except AttributeError:
    return


@client.command(aliases=['s'])
async def skip(ctx):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice == None:
    await ctx.reply("اول play کن")
  else:
    if len(db[sv_id]["songs"]) >= 1:
      del db[sv_id]["songs"][0]
      voice.stop()
      await play_music(ctx)
    else:
      voice.stop()
      await voice.disconnect()
      await ctx.reply("لیست آهنگ خالیه. شو بخیر")



@client.command()
async def qlist(ctx):
  sv_id = str(ctx.guild.id)
  song_num = 1
  des = ""
  if 'songs' in db[sv_id] and len(db[sv_id]['songs']) >= 1:
    for s in db[sv_id]['songs']:
      des += f"{str(song_num)}- {s}\n"
      song_num += 1
  embed = discord.Embed(title="لیست آهنگ ها", description=des, color=0x0057ba)
  await ctx.send(embed=embed)



@client.command()
async def lyrics(ctx):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  try:
    if sv_id in db and 'songs' in db[sv_id] and voice != None:
      song_name = db[sv_id]['songs'][0].replace(" ", "+")
      song = genius.search_song(song_name)
      l1 = str(song.lyrics).replace('EmbedShare URLCopyEmbedCopy','')
      lyrics = re.sub(r'\d+$', '', l1)
      lines = lyrics.splitlines()
      while len(lines) >= 1:
        l = []
        for x in range(50):
          if len(lines) >= 1:
            l.append(lines[0])
            del lines[0]
        l2 = "\n".join(l)
        embed = discord.Embed(title=f"متن آهنگ {db[sv_id]['songs'][0]}", description=l2, color=0x40218f)
        await ctx.send(embed=embed)
  except AttributeError:
    await ctx.send("متن این آهنگ موجود نیست.")




@client.command(aliases=['vol'])
async def volume(ctx, value):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  try:
     volume = float(value)
  except:
    return
  if voice != None:
    if 0 <= volume <= 100:
      v = volume/100
      voice.source.volume = v
      await ctx.send(f"میزان صدا به {int(volume)} تغییر پیدا کرد.")
      if sv_id in db:
        db[sv_id]['volume'] = v
    else:
      await ctx.send("باید یک عدد بین 0 تا 100 بزنی.")
  


    


@client.command()
async def go(ctx, time):
  sv_id = str(ctx.guild.id)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice != None:
    voice.stop()
    db[sv_id]['isgo'] = 'yes'
    t = int(time.split(':')[0])*60 + int(time.split(':')[1])
    await play_music(ctx, t)



@client.command()
async def recipe(ctx, n1, n2='', n3='', n4=''):
  l = []
  l.append(n1)
  if n2:
    l.append(n2)
  if n3:
    l.append(n3)
  if n4:
    l.append(n4)
  n = ' '.join(l)
  name = str(n1+n2+n3+n4).lower()
  formats = ['png', 'gif']
  collection = ['Basic', 'Tools', 'Blocks', 'Other', 'Defence', 'Brewing', 'Food', 'Mechanism', 'Dyes', 'Wool']
  is_searching = True
  while is_searching:
    for x in collection:
      for y in formats:
        url = f'https://www.minecraft-crafting.net/app/src/{x}/craft/craft_{name}.{y}'
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        s = str(soup.find('title'))
        if s != '<title>404 Not Found</title>':
          embed = discord.Embed(title=f'{n} Recipe')
          embed.set_image(url=url)
          await ctx.send(embed=embed)
          is_searching = False
    is_searching = False
  

@client.command()
async def voice(ctx, name):
  if str(name) == "آها":
    voiceChannel = ctx.message.author.voice.channel
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("aha.mp3"))
    await asyncio.sleep(3)
    await voice.disconnect()




#games

@client.command()
async def hangman(ctx):
  global words
  global hangmanPics
  sv_id = str(ctx.guild.id)
  if db[sv_id]['games']['currentGame'] == 'None' or 'games' not in db[sv_id] or sv_id not in db:
    if sv_id in db:
      if 'games' in db[sv_id]:
        db[sv_id]['games']['currentGame'] = 'hangman'
      else:
        db[sv_id]['games'] = {'currentGame': 'hangman'}
    else:
      db[sv_id] = {'games': {'currentGame': 'hangman'}}
    player = str(ctx.author)
    db[sv_id]['games']['player'] = player
    word = random.choice(words).upper()
    db[sv_id]['games']['hangman']['secret_word'] = word
    db[sv_id]['games']['hangman']['remain_letters'] = word
    db[sv_id]['games']['hangman']['used_letters'] = ''
    db[sv_id]['games']['hangman']['errors'] = 0
    db[sv_id]['games']['hangman']['letter_count'] = len(db[sv_id]['games']['hangman']['remain_letters'])
    if 'scores' not in db[sv_id]['games']['hangman']:
      db[sv_id]['games']['hangman']['scores'] = {player: 0}
    if player not in db[sv_id]['games']['hangman']['scores']:
      db[sv_id]['games']['hangman']['scores'][player] = 0
    while ' ' in db[sv_id]['games']['hangman']['secret_word'] or '-' in db[sv_id]['games']['hangman']['secret_word']:
      db[sv_id]['games']['hangman']['secret_word'] = random.choice(words).upper()
    dis_word = [letter if letter in db[sv_id]['games']['hangman']['used_letters'] else '-' for letter in word]
    embed = discord.Embed(title=' '.join(dis_word), color=0xf2ff00)
    embed.set_thumbnail(url='https://i.imgur.com/epiR9LC.png')
    await ctx.reply(embed=embed, mention_author=False)
    db[sv_id]['games']['timer'] = 180
    await game_timer(sv_id)
    
  else:
    await ctx.reply('هم اکنون در حال اجرای بازی می باشم.')


@client.command()
async def guess(ctx):
  sv_id = str(ctx.guild.id)
  if db[sv_id]['games']['currentGame'] == 'None' or 'currentGame' not in db[sv_id]['games'] or 'games' not in db[sv_id] or sv_id not in db:
    if sv_id in db:
      if 'games' in db[sv_id]:
        db[sv_id]['games']['currentGame'] = 'guess'
      else:
        db[sv_id]['games'] = {'currentGame': 'guess'}
    else:
      db[sv_id] = {'games': {'currentGame': 'guess'}}
    db[sv_id]['games']['player'] = str(ctx.author) 
    await ctx.reply("یه عدد بین 1 تا 1000 حدس بزن.")
    db[sv_id]['games']['guess']['secret_num'] = random.randint(1,1001)
    db[sv_id]['games']['guess']['current_score'] = 0
    db[sv_id]['games']['timer'] = 30
    await game_timer(sv_id)
  else:
    await ctx.reply('هم اکنون در حال اجرای بازی می باشم.')


@client.command()
async def scores(ctx, game: str):
  sv_id = str(ctx.guild.id)
  scores = ''
  try:
    list = {k: v for k, v in sorted(db[sv_id]['games'][game]['scores'].items(), key=lambda item: item[1])[::-1]}
  except KeyError:
    await ctx.send('امتیازی ثبت نشده.')
    return
  if game == 'guess':
    title = 'کمترین تعداد حدس ها'
    list = {k: v for k, v in sorted(db[sv_id]['games'][game]['scores'].items(), key=lambda item: item[1])}
  elif game == 'hangman':
    title = 'امتیاز ها'
  for s in list:
      s_list = str(s.split('#', 1)[0]) + ": " + str(list[s])
      scores += s_list + "\n"
  embed = discord.Embed(title=title, description=scores, color=0x90ee90)
  await ctx.send(embed=embed)
  
@client.command()
async def help(ctx):
  await ctx.reply("لیست دستورات:" + "\n\n" +
                  "Games:" + "\n" + 
                 "-guess" + "\n" + 
                 "-hangman" + "\n" +
                 "-scores" + "\n"
                 "-randomgame" + "\n" +
                 "-recipe" + "\n\n" +
                 "Music:" + "\n" +
                 "-queue" + "\n" + 
                 "-play" + "\n" + 
                 "-skip" + "\n" +
                 "-stop" + "\n" +
                 "-qlist" + "\n" +
                 "-volume" + "\n" +
                 "-lyrics" + "\n" + 
                 "-go" + "\n\n" + 
                 "Filters:" + "\n" +
                 "-add" + "\n" +
                 "-del" + "\n" +
                 "-list")

@client.command()
async def test(ctx):
  char_list = ['!', '@', '#', '$', '%', '&', '*']
  row1 = random.choice(char_list)
  row2 = random.choice(char_list)
  row3 = random.choice(char_list)
  msg = await ctx.send(f"{row1}  {row2}  {row3}")
  for i in range(20):
    await asyncio.sleep(0.8)
    row1 = random.choice(char_list)
    row2 = random.choice(char_list)
    row3 = random.choice(char_list)
    await msg.edit(content = f"{row1}  {row2}  {row3}")




keep_alive()
client.run(os.getenv('TOKEN'))

