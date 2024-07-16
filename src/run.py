import discord, aiohttp
import os, dotenv
import auth
import json

dotenv.load_dotenv()
bot = discord.Bot()

CURRENT_SEASON = '52ca6698-41c1-e7de-4008-8994d2221209'

@bot.event
async def on_ready():
    print(f"{bot.user} up and ready!")

    # Load authorization headers / API keys
    bot.API = {
        "Authorization": f"{os.getenv('API')}"
    }
    tokens = await auth.load_cred()
    if tokens != None:
        bot.HEADERS = {
            "X-Riot-Entitlements-JWT": f"{tokens.entitlements_token}",
            "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            "X-Riot-ClientVersion": "release-09.00-shipping-28-2628993",
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
        }
    
    bot.players = { }

    # Load PUUIDs of registered players
    try:
        with open('players.json', 'r') as f:
            bot.players = json.load(f)
    except:
        print("Reading error occured. Making new file...")
        with open('players.json', 'w') as f:
            bot.players = {}



@bot.slash_command(name="hello", description="Make sure bot is breathing")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hi :)")

@bot.slash_command(name="check", description="Check out a player's stats")
async def check(ctx: discord.ApplicationContext, player: str, tag: str):
    data = None

    if len(player) > 16 or len(player) < 3 or len(tag) == 0:
        await ctx.respond("Please put a valid length username and tag")

    elif f"{player}#{tag}" not in bot.players:
        if tag[0] == '#':
            tag = tag[1:]

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.henrikdev.xyz/valorant/v1/account/{player}/{tag}", headers=bot.API) as r:
                if r.status == 200:
                    data = await r.json()

                    bot.players[f"{player}#{tag}"] = data['data']
                    with open('players.json', 'w', encoding='utf-8') as f:
                        json.dump(bot.players, f, indent=4)
                    await ctx.respond(data)
                    await ctx.respond(bot.players)
                else:
                    await ctx.respond("i broke")
                    print(r.text)

    else:
        data = bot.players[f"{player}#{tag}"]
        # Send to data embedder -> send
        embed = await formatter(player, tag, data)
        await ctx.respond(embed=embed)


async def formatter(player: str, tag: str, player_data: json):
    embed = discord.Embed(
        title=f"{player}",
        color=discord.Color.dark_blue()
    )

    puuid = player_data['puuid']

    embed.set_footer(text="If you see this, hi") # footers can have icons too
    embed.set_author(name=f"#", icon_url=f"{player_data['card']['small']}")
    embed.set_thumbnail(url=f"{player_data['card']['large']}")

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://pd.na.a.pvp.net/mmr/v1/players/{puuid}/', headers=bot.HEADERS) as r:
            if r.status == 200:
                data = await r.json(content_type=None)
                formatted = data['QueueSkills']['competitive']['SeasonalInfoBySeasonID'][CURRENT_SEASON]
                formatted = clean_info(formatted)
                embed.add_field(name="Current Season Info", value=formatted, inline=True)
                
                return embed
            else:
                embed.add_field(name="Current Season Info", value="Something went wrong", inline=True)
                print(r.text)
                print(r.json(content_type=None))
                return embed

def clean_info(unf):
    wins = unf['NumberOfWins']
    games = unf['NumberOfGames']
    wr = round(((float(wins) / float(games)) * 100), 1)

    res = f"""**Wins: {wins}**
              Games: {games}
              Winrate: {wr}%
              Rank: {unf['Rank']}"""
    
    return res


bot.run(os.getenv('TOKEN'))