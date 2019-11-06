import api, discord
from discord.utils import get as get_role
import auth, json
client = discord.Client()

class StatServer:
    def __init__(self, server):
        self.server = server
        self.config = api.Config("ow-configs", self.server.id)

#api.Api().get(api.STATS_ROUTE.format("TheTimebike-2349"))
#serv = StatServer("123")
#serv.config.update("role", "support")

@client.event
async def on_server_join(server):
    statserv = StatServer(server)

@client.event
async def on_message(message):
    serv = StatServer(message.author.server)
    config = serv.config.load()

    if serv.config.load()["members"].get(message.author.id, None) == None:
        new_members = serv.config.load()["members"]
        new_members[message.author.id] = [None, None]
        serv.config.update("members", new_members)

    if message.content.lower().startswith(".register "):
        username = message.content[len(".register "):]
        new_members = serv.config.load()["members"]
        new_members[message.author.id][0] = username.replace("#", "-")
        serv.config.update("members", new_members)
        await client.send_message(message.channel, "Config Updated! Your account is now bound to **{0}**".format(username))

    if message.content.lower().startswith(".platform "):
        platform = message.content.lower()[len(".register "):]
        if platform not in ["pc", "psn", "xbl"]:
            await client.send_message(message.channel, "Please select a platform from the following :\n**PC**, **PSN** or **XBL**")
            return
        new_members = serv.config.load()["members"]
        new_members[message.author.id][1] = platform
        serv.config.update("members", new_members)
        await client.send_message(message.channel, "Config Updated! Your account is now bound to **{0}**".format(platform))

    if message.content.lower().startswith(".config achievement "):
        achievements = message.content.lower()[len(".config achievement "):].replace(" "+message.role_mentions[0].mention, "").split(", ")
        for achievement in achievements:
            if achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"]:
                await client.send_message(message.channel, "Achievement {0} found!".format(achievement.title()))
                serv.config.update(achievement.replace(" ", "_"), message.role_mentions[0].id)
            else:
                await client.send_message(message.channel, "Achievement {0} not found!".format(achievement.title()))
        print(achievements)

    elif message.content.lower().startswith(".config region "):
        new_region = message.content.lower()[len(".config region "):]
        if new_region not in ["kr", "eu", "us"]:
            await client.send_message(message.channel, "Please select a region from the following: \n**KR**, **EU** or **US**.")
            return
        serv.config.update("region", new_region)
        await client.send_message(message.channel, "Config Updated! Your new region is **{0}**.".format(new_region.upper()))


    elif message.content.lower().startswith(".config role "):
        new_role = message.content.lower()[len(".config role "):]
        if new_role not in ["support", "tank", "damage"]:
            await client.send_message(message.channel, "Please select a role from the following: \n**SUPPORT**, **TANK** or **DAMAGE**.")
            return
        serv.config.update("role", new_role)
        await client.send_message(message.channel, "Config Updated! Your new role is **{0}**.".format(new_role.title()))

    elif message.content.lower().startswith(".config rank roles "):
        bronze_id = message.role_mentions[0].id
        serv.config.update("bronze_id", bronze_id)

        silver_id = message.role_mentions[1].id
        serv.config.update("silver_id", silver_id)

        gold_id = message.role_mentions[2].id
        serv.config.update("gold_id", gold_id)

        platinum_id = message.role_mentions[3].id
        serv.config.update("platinum_id", platinum_id)
        
        diamond_id = message.role_mentions[4].id
        serv.config.update("diamond_id", diamond_id)

        master_id = message.role_mentions[5].id
        serv.config.update("master_id", master_id)

        grandmaster_id = message.role_mentions[6].id
        serv.config.update("grandmaster_id", grandmaster_id)

        await client.send_message(message.channel, "Config Updated! Those roles have been set for the competitive rank roles.")

    elif message.content.lower().startswith(".config bronze "):
        role_id = message.role_mentions[0].id
        serv.config.update("bronze_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new bronze role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config silver "):
        role_id = message.role_mentions[0].id
        serv.config.update("silver_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new bronze role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config gold "):
        role_id = message.role_mentions[0].id
        serv.config.update("gold_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new silver role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config platinum "):
        role_id = message.role_mentions[0].id
        serv.config.update("platinum_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new platinum role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config diamond "):
        role_id = message.role_mentions[0].id
        serv.config.update("diamond_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new diamond role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config master "):
        role_id = message.role_mentions[0].id
        serv.config.update("master_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new master role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config grandmaster "):
        role_id = message.role_mentions[0].id
        serv.config.update("grandmaster_id", role_id)
        await client.send_message(message.channel, "Config Updated! Your new grandmaster role is **{0}**".format(message.role_mentions[0].mention))

    elif message.content.lower().startswith(".config"):
        config = serv.config.load()
        embed=discord.Embed()
        embed=discord.Embed(title="Ow Bot Config", description="Configuration for the OW Role Bot")
        embed.add_field(name="Region\nRole", value="** **", inline=True)
        embed.add_field(name="{0}\n{1}".format(config["region"].upper(), config["role"].title()), value="** **", inline=True)
        embed.set_footer(text="Made by u/TheTimebike")
        await client.send_message(message.channel, embed=embed)

    elif config["members"][message.author.id][0] != None:
        stats = api.Api().get(api.STATS_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        print(json.dumps(stats, indent=4))
        rank = stats[config["region"]]["stats"]["competitive"]["overall_stats"]["{0}_tier".format(config["role"])]
        to_remove, ranks = [], ["bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster"]
        for rank_name in ranks:
            if rank_name.lower() != rank.lower():
                to_remove.append(get_role(message.author.server.roles, id=config["{0}_id".format(rank_name)]))

        for _ in to_remove:
            await client.remove_roles(message.author, to_remove[0], to_remove[1], to_remove[2], to_remove[3], to_remove[4], to_remove[5])
        await client.add_roles(message.author, get_role(message.author.server.roles, id=config["{0}_id".format(rank)]))

        achievements = api.Api().get(api.ACHIEVEMENT_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        for role, achievement_block in achievements[config["region"]]["achievements"].items():
            for achievement, state in achievement_block.items():
                if state == True and config.get(achievement, None) != None:
                    await client.add_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))
                if state == False and config.get(achievement, None) != None:
                    await client.remove_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))

client.run(auth.token)