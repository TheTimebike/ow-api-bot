import api, discord
from discord.utils import get as get_role
import auth, json
client = discord.Client()

class StatServer:
    def __init__(self, server):
        self.server = server
        self.config = api.Config("ow-configs", self.server.id)
        
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
        achievements = message.content.lower()[len(".config achievement "):].split(", ")
        achievement_conversion_table = serv.config.get_conversion_table("hero_details")
        for achievement in achievements:
            if achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"]:
                new_role_obj = await client.create_role(message.author.server, name=achievement.title())
                serv.config.update(achievement.replace(" ", "_"), new_role_obj.id)
                await client.send_message(message.channel, "I will give the {0} role for the achievement: {1}!".format(new_role_obj.name, achievement.title()))
            elif achievement in achievement_conversion_table.keys():
                for achievement in achievement_conversion_table[achievement]["achievements"]:
                     new_role_obj = await client.create_role(message.author.server, name=achievement.title())
                     serv.config.update(achievement.replace(" ", "_"), new_role_obj.id)
            for name, hero_block in achievement_conversion_table.items():
                if achievement in hero_block["type"]:
                     for achievement in achievement_conversion_table[achievement]["achievements"]:
                     new_role_obj = await client.create_role(message.author.server, name=achievement.title())
                     serv.config.update(achievement.replace(" ", "_"), new_role_obj.id)
                    
            else:
                await client.send_message(message.channel, "Achievement {0} not found! Please check spelling and try again".format(achievement.title()))
        print(achievements)

    elif message.content.lower().startswith(".config disable achievement "):
        achievements_to_disable = message.content.lower()[len(".config disable achievement "):].split(", ")
        for achievement in achievements_to_disable:
            if achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"] and in serv.config.load().keys():
                serv.config.delete_achievement(achievement.replace(" ", "_"))
                await client.send_message(message.channel, "The achievement {0} will no longer give a role!".format(achievement.title()))
            elif achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"] and not in serv.config.load().keys()"
                await client.send_message(message.channel, "Could not find the achievement: {0}.".format(achievement.title()))
                
    elif message.content.lower().startswith(".config time "):
        arg = message.content.lower()[len(".config time "):].split(", ")
        time = arg[1]
        hero = arg[0]
        role_name = "{0} Hour {1} Playtime".format(time, hero)
        new_role_obj = await client.create_role(message.author.server, name=role_name.title())
        if config["time"].get(hero, None) == None:
            config["time"][hero] = {}
        config["time"][hero][time] = new_role_obj.id
        serv.config.update("time", config["time"])

    elif message.content.lower().startswith(".config disable time "):
        arg = message.content.lower()[len(".config disable time "):].split(", ")
        time = arg[1]
        hero = arg[0]
        if config["time"].get(hero, None) != None and config["time"][hero].get(time, None) != None:
            serv.config.delete_time_role(hero, time)
            await client.send_message(message.channel, "The {0} hours playtime role for {1} has been disabled.".format(time, hero.title()))
        else:
            await client.send_message(message.channel, "The {0} hours playtime role for {1} was not found, please check your spelling and try again".format(time, hero.title()))
        
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
        bronze_role_obj = await client.create_role(message.author.server, name="Bronze")
        silver_role_obj = await client.create_role(message.author.server, name="Silver)
        gold_role_obj = await client.create_role(message.author.server, name="Gold")
        platinum_role_obj = await client.create_role(message.author.server, name="Platinum")
        diamond_role_obj = await client.create_role(message.author.server, name="Diamond")
        master_role_obj = await client.create_role(message.author.server, name="Master")
        grandmaster_role_obj = await client.create_role(message.author.server, name="Grandmaster")
        
        serv.config.update("bronze_id", bronze_role_obj.id)
        serv.config.update("silver_id", silver_role_obj.id)
        serv.config.update("gold_id", gold_role_obj.id)
        serv.config.update("platinum_id", platinum_role_obj.id)
        serv.config.update("diamond_id", diamond_role_obj.id)
        serv.config.update("master_id", master_role_obj.id)
        serv.config.update("grandmaster_id", grandmaster_role_obj.id)

        await client.send_message(message.channel, "Config Updated! New roles have been created for the competitive rank roles. Be sure to configure their colours, positions and names!")

    elif message.content.lower().startswith(".config bronze "):
        role = await client.create_role(message.author.server, name="Bronze")
        serv.config.update("bronze_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new bronze role is **{0}**".format(message.role.mention))

    elif message.content.lower().startswith(".config silver "):
        role = await client.create_role(message.author.server, name="Silver")
        serv.config.update("silver_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new silver role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config gold "):
        role = await client.create_role(message.author.server, name="Gold")
        serv.config.update("gold_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new gold role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config platinum "):
        role = await client.create_role(message.author.server, name="Platinum")
        serv.config.update("platinum_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new platinum role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config diamond "):
        role = await client.create_role(message.author.server, name="Diamond")
        serv.config.update("diamond_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new diamond role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config master "):
        role = await client.create_role(message.author.server, name="Master")
        serv.config.update("master_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new master role is **{0}**.Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config grandmaster "):
        role = await client.create_role(message.author.server, name="Grandmaster")
        serv.config.update("grandmaster_id", role.id)
        await client.send_message(message.channel, "Config Updated! Your new grandmaster role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))

    elif message.content.lower().startswith(".config"):
        config = serv.config.load()
        embed=discord.Embed()
        embed=discord.Embed(title="Ow Bot Config", description="Configuration for the OW Role Bot")
        embed.add_field(name="Role", value="** **", inline=True)
        embed.add_field(name="{0}".format(config["role"].title()), value="** **", inline=True)
        embed.set_footer(text="Made by u/TheTimebike")
        await client.send_message(message.channel, embed=embed)

    elif config["members"][message.author.id][0] != None:
        stats = api.Api().get(api.STATS_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        rank = stats["stats"]["competitive"]["overall_stats"]["{0}_tier".format(config["role"])]
        to_remove, ranks = [], ["bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster"]
        for rank_name in ranks:
            if rank_name.lower() != rank.lower():
                to_remove.append(get_role(message.author.server.roles, id=config["{0}_id".format(rank_name)]))

        for _ in to_remove:
            await client.remove_roles(message.author, to_remove[0], to_remove[1], to_remove[2], to_remove[3], to_remove[4], to_remove[5])
        await client.add_roles(message.author, get_role(message.author.server.roles, id=config["{0}_id".format(rank)]))

        achievements = api.Api().get(api.ACHIEVEMENT_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        for role, achievement_block in achievements["achievements"].items():
            for achievement, state in achievement_block.items():
                if state == True and config.get(achievement, None) != None:
                    await client.add_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))
                if state == False and config.get(achievement, None) != None:
                    await client.remove_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))

        playtime = api.Api().get(api.HEROES_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        for hero, playtime_block in config["time"].items():
            overall_hero_playtime = playtime["heroes"]["playtime"]["quickplay"].get(hero, 0) +  playtime["heroes"]["playtime"]["competitive"].get(hero, 0)
            print(overall_hero_playtime)
            for key, attr in playtime_block.items():
                print(key)
                if int(overall_hero_playtime) >= int(key):
                    await client.add_roles(message.author, get_role(message.author.server.roles, id=attr))
client.run(auth.token)
