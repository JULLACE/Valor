import discord, dotenv, os, aiohttp, json

dotenv.load_dotenv()
bot = discord.Bot()

# TODO: Grab remotely
CURRENT_SEASON = '52ca6698-41c1-e7de-4008-8994d2221209'

HEADERS = {
    "X-Riot-Entitlements-JWT": os.getenv('JWT'),
    "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
    "X-Riot-ClientVersion": "release-09.00-shipping-28-2628993",
    "Authorization": os.getenv('AUTH')
}

@bot.event
async def on_ready():
    print(f"{bot.user} up and ready!")

@bot.slash_command(name="hello", description="Make sure bot is breathing")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hi :)")

@bot.slash_command(name="register", description="Register a player for the bot to track")
async def register(ctx: discord.ApplicationContext, player: str):
    ctx.respond("WIP")

@bot.slash_command(name="check", description="Check out a player's stats")
async def check(ctx: discord.ApplicationContext, player: str):
    embed = discord.Embed(
        title="Minos",
        color=discord.Color.dark_blue()
    )

    embed.set_footer(text="If you see this, hi") # footers can have icons too
    embed.set_author(name="Player's Info", icon_url="https://pbs.twimg.com/media/Fbb1PYFagAA6579.png")
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/ficcion-sin-limites/images/d/d8/Minos_Phrime.png/revision/latest/scale-to-width-down/600?cb=20230906001709&path-prefix=es")

    async with aiohttp.ClientSession() as session:
        async with session.get('https://pd.na.a.pvp.net/mmr/v1/players/18f595d7-ec04-513c-bcf5-53d6914f9a53', headers=HEADERS) as r:
            if r.status == 200:
                data = await r.json(content_type=None)
                formatted = data['QueueSkills']['competitive']['SeasonalInfoBySeasonID'][CURRENT_SEASON]
                formatted = clean_info_season(formatted)

                embed.add_field(name="Current Season Info", value=formatted, inline=True)
                
                await ctx.respond(embed=embed)
            else:
                await ctx.respond("i require assistance")
                print(r.text)

def clean_info_season(unf):
    wins = unf['NumberOfWins']
    games = unf['NumberOfGames']
    wr = round(((float(wins) / float(games)) * 100), 1)

    res = f"""**Wins: {wins}**
              Games: {games}
              Winrate: {wr}%
              Rank: {unf['Rank']}"""
    
    return res


bot.run(os.getenv('TOKEN'))