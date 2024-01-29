import discord
from discord.ext import commands
import cloudscraper
from bs4 import BeautifulSoup
import requests
import os
import json

base_url = "https://gamerdvr.com/games/fortnite/screenshots"
scraper = cloudscraper.create_scraper()
num_pages = 5

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='scrape')
async def scrape(ctx):
    data = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        screenshots = soup.find_all('li', class_='capture-container')

        for screenshot in screenshots:
            data.append({
                "views": screenshot['data-views'],
                "gamertag": screenshot['data-g-fname'].split('/')[-1].split('.')[0] or "N/A",
                "url": screenshot.find('img', class_='video-image')['data-original'] or "N/A",
                "user": "Xbox" if screenshot.find('a', class_='').text.lower() == 'fortnite' else screenshot.find('a', class_='').text or "N/A",
                "date": screenshot.find('small', class_='').text or "N/A"
            })

            if screenshot['data-views'] < '10' and screenshot.find('small', class_='').text.split('/')[-1] == '2018':
                embed = discord.Embed(title="Fortnite Scrapper",
                                      description=f"Views: {screenshot['data-views']} | Gamertag: {screenshot['data-g-fname'].split('/')[-1].split('.')[0]} | User: {'Xbox' if screenshot.find('a', class_='').text.lower() == 'fortnite' else screenshot.find('a', class_='').text} | Date: {screenshot.find('small', class_='').text}",
                                      color=discord.Color.red())
                embed.set_image(url=screenshot.find('img', class_='video-image')['data-original'])
                await ctx.send(embed=embed)

                img_data = requests.get(screenshot.find('img', class_='video-image')['data-original']).content
                images_directory = 'images'
                if not os.path.exists(images_directory):
                    os.makedirs(images_directory)

                with open(images_directory + '/' + screenshot['data-g-fname'], 'wb') as handler:
                    handler.write(img_data)

    json_filename = 'scraped_data.json'
    with open(json_filename, 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    await ctx.send(f"Scraped data saved to {json_filename}")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('YOUR_BOT_TOKEN')
