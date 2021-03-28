import discord
from google.cloud import vision
import requests
import io
import os

client = discord.Client()
clientGoogle = vision.ImageAnnotatorClient()


TOKEN = "Bot Token Goes Here"

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if (message.author.bot == False):
    attachments = message.attachments
  
    if(len(attachments) > 0):
      url = attachments[0]
      with open(url.filename, 'wb') as handle:
        response = requests.get(url.url, stream = True)
        messageAuthor = message.author.name
        await message.delete()
        
        if not response.ok:
          print(response)
        
        for block in response.iter_content(1024):
          if not block:
            break
          handle.write(block)

      file_name = os.path.abspath(url.filename)
      with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
      image = vision.Image(content=content)

      response = clientGoogle.safe_search_detection(image=image)
      labels = response.safe_search_annotation
      likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')
        
      if response.error.message:
        raise Exception('{}\nFor more info on error messages, check: ''https://cloud.google.com/apis/design/errors'.format(response.error.message))

      if (likelihood_name[labels.adult] == "LIKELY" or likelihood_name[labels.adult] == "VERY_LIKELY"):
        await message.channel.send("MESSAGE posted by %s DELETED for: Adult Content" % messageAuthor)
      elif (likelihood_name[labels.racy] == "LIKELY" or likelihood_name[labels.racy] == "VERY_LIKELY"):
        await message.channel.send("MESSAGE posted by %s DELETED for: Racy Content" % messageAuthor)
      elif (likelihood_name[labels.violence] == "LIKELY" or likelihood_name[labels.violence] == "VERY_LIKELY"):
        await message.channel.send("MESSAGE posted by %s DELETED for: Violent Content" % messageAuthor)
      elif (likelihood_name[labels.medical] == "LIKELY" or likelihood_name[labels.medical] == "VERY_LIKELY"):
        await message.channel.send("Message posted by %s DELETED for: Medical Content" % messageAuthor)
      else:
        await message.channel.send(str("Posted by: %s" % messageAuthor), file = discord.File(url.filename))
        #await message.channel.send(str("Posted by: %s" % messageAuthor))
        

client.run(TOKEN)
