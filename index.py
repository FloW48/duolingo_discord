import discord
import duolingo
import json
import asyncio
import datetime as dt
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType, CommandOnCooldown

usernameDuolingo = ''
passwordDuolingo = ''
tokenDiscord = ''

with open('secret.txt', 'r') as file:
    data = file.read().splitlines()
    usernameDuolingo = data[0]
    passwordDuolingo = data[1]
    tokenDiscord = data[2]


lingo = duolingo.Duolingo(usernameDuolingo, passwordDuolingo)
bot = commands.Bot(command_prefix='duol ')

cooldownRanking = 0
timeDailyRanking = 22


@bot.event
async def on_ready():
    print(dt.datetime.now().hour)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your progress"))
    await loadUsersInFile()
    dailyLeaderBoard.start()

async def loadUsersInFile():
    ans = str(lingo.get_friends())
    with open('users.txt', 'w') as file:
        file.write(ans)

@tasks.loop(hours=24)
async def dailyLeaderBoard():
    global lingo
    file = open("users.txt", mode="r")
    users = file.read()
    file.close()
    users = users.replace("'", "\"")
    usersFileDic = json.loads(users)

    lingo = duolingo.Duolingo(usernameDuolingo, passwordDuolingo)
    ans = str(lingo.get_friends())
    # ans = '[{"username": "FloW48_", "id": 670694569, "points": 7600, "languages": []}, {"username": "lucaasmth", "id": 25231199, "points": 3600, "languages": []}, {"username": "DogMage", "id": 718168090, "points": 410, "languages": []}, {"username": "FloWBotz", "id": 720422604, "points": 100, "languages": []}]'
    ans = ans.replace("'", "\"")
    dic = json.loads(ans)

    for i in range(0, len(usersFileDic)):
        if(usersFileDic[i]["username"] == dic[i]["username"] and usersFileDic[i]["username"] != "FloWBotz"):
            dic[i]["points"] = dic[i]["points"] - usersFileDic[i]["points"]

    dic = sorted(dic, key=lambda item: item.get("points"))
    dic.reverse()   

    embed = discord.Embed()
    embed.set_author(name="FloW")
    embed.title = "Daily Ranking duolingo"
    for i in range(0, len(dic)):
        if dic[i]["username"] != "FloWBotz":
            embed.add_field(name=str(i+1)+" - "+dic[i]["username"], value=">>> "+str(dic[i]["points"])+" xp", inline=False)
    channel = await bot.fetch_channel('797563311045869628')
    await channel.send(embed=embed)
    ans.replace("\"", "'")
    with open("users.txt", "w") as file:
        file.write(ans)
    print("daily end")


@dailyLeaderBoard.before_loop
async def before_dailyLeadeBoard():
    global timeDailyRanking
    for _ in range(60*60*24):  # loop the hole day
        if (dt.datetime.now().hour+1)%24 == timeDailyRanking:  # 24 hour format
            print('It is time')
            return
        await asyncio.sleep(1)# wait a second before looping again. You can make it more


@bot.command()
async def ranking(ctx):
    global cooldownRanking
    global lingo
    if(cooldownRanking == 0):
        lingo = duolingo.Duolingo(usernameDuolingo, passwordDuolingo)
        ans = str(lingo.get_friends())
        ans = ans.replace("'", "\"")
        dic = json.loads(ans)
        dic = sorted(dic, key=lambda item: item.get("points"))
        dic.reverse()   
        embed = discord.Embed()
        embed.set_author(name="FloW")
        embed.title = "Ranking duolingo"
        i = 0
        for user in dic:
            i += 1
            if user["username"] != "FloWBotz":
                embed.add_field(name=str(i)+" - "+user["username"], value=">>> "+str(user["points"])+" xp", inline=False)
        await ctx.send(embed=embed)
        cooldownRanking = 3600
        while cooldownRanking != 0:
            cooldownRanking -= 1
            await asyncio.sleep(1)
        cooldownRanking = True
    else:
        await ctx.send("Commande en cooldown : %d s" %cooldownRanking)

@bot.command()
async def time(ctx, msg):
    global timeDailyRanking
    try:
        time = int(msg)
        if(time >= 0 and time <= 23):
            timeDailyRanking = time
            await ctx.send("Le temps a été modifié a %d, temps actuel : %d" %(timeDailyRanking,(dt.datetime.now().hour+1)%24))
        else:
            await ctx.send("Voud devez entrez une heure entre 0 et 23")
    except ValueError:
        await ctx.send("Merci d'entrez un **nombre** entre 0 et 23")

bot.run(tokenDiscord)

