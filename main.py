import api, discord
from discord.utils import get as get_role
import auth, json
from time import sleep
client = discord.Client()

class StatServer:
    def __init__(self, server):
        self.server = server
        self.config = api.Config("ow-configs", self.server.id)
        
@client.event
async def on_role_delete(role):
    serv = StatServer(role.server)
    config = serv.config.load()
    for key, attr in config.items():
        if attr == role.id:
            config[key] == None
    serv.config.save(config)
    for hero, time_block in config["time"].items():
        for time, role_id in time_block.items():
            if role_id == role.id:
                serv.config.delete_time_role(hero, time)
@client.event
async def on_server_join(server):
    statserv = StatServer(server)

@client.event
async def on_message(message):
    print("{0} -- {1}".format(message.author.display_name, message.content))
    serv = StatServer(message.author.server)
    config = serv.config.load()

    #if message.author.id == "261926271892717569" and message.content.lower().startswith("remove roles"):
    #    for role in message.author.server.roles:
    #        if role.name.lower() != "bot" and role.name.lower() != "@everyone":
    #            await client.delete_role(message.author.server, role)

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
        platform = message.content.lower()[len(".platform "):]
        if platform not in ["pc", "psn", "xbl"]:
            await client.send_message(message.channel, "Please select a platform from the following :\n**PC**, **PSN** or **XBL**")
            return
        new_members = serv.config.load()["members"]
        new_members[message.author.id][1] = platform
        serv.config.update("members", new_members)
        await client.send_message(message.channel, "Config Updated! Your account is now bound to **{0}**".format(platform))

    if message.content.lower().startswith(".config achievement ") and message.author.server_permissions.administrator:
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
                    await client.send_message(message.channel, "Created role for achievement {0}".format(achievement.title()))   
            else:
                await client.send_message(message.channel, "Achievement {0} not found! Please check spelling and try again".format(achievement.title()))
            for name, hero_block in achievement_conversion_table.items():
                if achievement in hero_block["type"] or achievement == "all":
                    for achievement_new in achievement_conversion_table[name]["achievements"]:
                        new_role_obj = await client.create_role(message.author.server, name=achievement_new.title())
                        serv.config.update(achievement_new.replace(" ", "_"), new_role_obj.id)
                        await client.send_message(message.channel, "Created role for achievement {0}".format(achievement_new.title()))   

    elif message.content.lower().startswith(".config disable achievement ") and message.author.server_permissions.administrator:
        achievements_to_disable = message.content.lower()[len(".config disable achievement "):].split(", ")
        achievement_conversion_table = serv.config.get_conversion_table("hero_details")
        for achievement in achievements_to_disable:
            if achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"] and achievement.replace(" ", "_") in serv.config.load().keys():
                serv.config.delete_achievement(achievement.replace(" ", "_"))
                await client.send_message(message.channel, "The achievement {0} will no longer give a role!".format(achievement.title()))
            elif achievement.replace(" ", "_") in serv.config.get_conversion_table("achievements")["all"] and achievement.replace(" ", "_") not in serv.config.load().keys():
                await client.send_message(message.channel, "Could not find the achievement: {0}.".format(achievement.title()))
            elif achievement in achievement_conversion_table.keys():
                for achievement_new in achievement_conversion_table[achievement]["achievements"]:
                    if achievement_new in serv.config.load().keys():
                        serv.config.delete_achievement(achievement_new.replace(" ", "_"))
                        await client.send_message(message.channel, "The achievement {0} will no longer give a role".format(achievement_new.replace(" ", "_").title()))   
            elif achievement == "all":
                for name, achievement_block in achievement_conversion_table.items():
                    for achievement_new in achievement_block["achievements"]:
                        achievement_new = achievement_new.replace(" ", "_")
                        if achievement_new in serv.config.load().keys():
                            serv.config.delete_achievement(achievement_new.replace(" ", "_"))
                            await client.send_message(message.channel, "The achievement {0} will no longer give a role".format(achievement_new.replace("_", " ").title())) 
            else:
                print("could not find {0}".format(achievement))
        for name, hero_block in achievement_conversion_table.items():
            if achievement in hero_block["type"] or achievement == "all" and achievement in serv.config.load().keys():
                for achievement_new in achievement_conversion_table[name]["achievements"]:
                    serv.config.delete_achievement(achievement_new.replace(" ", "_"))
                    await client.send_message(message.channel, "The achievement {0} will no longer give a role!".format(achievement_new.title()))   

    elif message.content.lower().startswith(".config time ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            arg = message.content.lower()[len(".config time "):].split(", ")
        elif len(message.role_mentions) == 1:
            arg = message.content.lower()[len(".config time "):].replace(message.role_mentions[0].mention, "").split(", ")
        time = arg[1]
        hero = arg[0]
        role_name = "{0} Hour {1} Playtime".format(time, hero)
        if len(message.role_mentions) == 0:
            new_role_obj = await client.create_role(message.author.server, name=role_name.title())
        elif len(message.role_mentions) == 1:
            new_role_obj = message.role_mentions[0]
        if config["time"].get(hero, None) == None:
            config["time"][hero] = {}
        config["time"][hero][time] = new_role_obj.id
        serv.config.update("time", config["time"])
        await client.send_message(message.channel, "The {0} hours playtime role for {1} has been bound.".format(time, hero.title()))

    elif message.content.lower().startswith(".config disable time ") and message.author.server_permissions.administrator:
        arg = message.content.lower()[len(".config disable time "):].split(", ")
        time = arg[1]
        hero = arg[0]
        if config["time"].get(hero, None) != None and config["time"][hero].get(time, None) != None:
            serv.config.delete_time_role(hero, time)
            await client.send_message(message.channel, "The {0} hours playtime role for {1} has been disabled.".format(time, hero.title()))
        else:
            await client.send_message(message.channel, "The {0} hours playtime role for {1} was not found, please check your spelling and try again".format(time, hero.title()))
        
    elif message.content.lower().startswith(".config role ") and message.author.server_permissions.administrator:
        new_role = message.content.lower()[len(".config role "):]
        if new_role not in ["support", "tank", "damage"]:
            await client.send_message(message.channel, "Please select a role from the following: \n**SUPPORT**, **TANK** or **DAMAGE**.")
            return
        serv.config.update("role", new_role)
        await client.send_message(message.channel, "Config Updated! Your new role is **{0}**.".format(new_role.title()))

    elif message.content.lower().startswith(".config rank roles") and message.author.server_permissions.administrator:
        grandmaster_role_obj = await client.create_role(message.author.server, name="Grandmaster", hoist=True)
        master_role_obj = await client.create_role(message.author.server, name="Master", hoist=True)
        diamond_role_obj = await client.create_role(message.author.server, name="Diamond", hoist=True)
        platinum_role_obj = await client.create_role(message.author.server, name="Platinum", hoist=True)
        gold_role_obj = await client.create_role(message.author.server, name="Gold", hoist=True)
        silver_role_obj = await client.create_role(message.author.server, name="Silver", hoist=True)
        bronze_role_obj = await client.create_role(message.author.server, name="Bronze", hoist=True)
        
        serv.config.update("bronze_id", bronze_role_obj.id)
        serv.config.update("silver_id", silver_role_obj.id)
        serv.config.update("gold_id", gold_role_obj.id)
        serv.config.update("platinum_id", platinum_role_obj.id)
        serv.config.update("diamond_id", diamond_role_obj.id)
        serv.config.update("master_id", master_role_obj.id)
        serv.config.update("grandmaster_id", grandmaster_role_obj.id)

        await client.send_message(message.channel, "Config Updated! New roles have been created for the competitive rank roles. Be sure to configure their colours, positions and names!")

    elif message.content.lower().startswith(".config bronze ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Bronze", hoist=True)
            serv.config.update("bronze_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new bronze role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("bronze_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new bronze role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable bronze") and message.author.server_permissions.administrator:
        serv.config.update("bronze_id", None)
        await client.send_message(message.channel, "The bronze role has been disabled.")
            
    elif message.content.lower().startswith(".config silver ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Silver", hoist=True)
            serv.config.update("silver_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new silver role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("silver_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new silver role is **{0}**. Be sure to configure its colour, position and name!".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable silver") and message.author.server_permissions.administrator:
        serv.config.update("silver_id", None)
        await client.send_message(message.channel, "The silver role has been disabled.")
            
    elif message.content.lower().startswith(".config gold ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Gold", hoist=True)
            serv.config.update("gold_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new gold role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("gold_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new gold role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable gold") and message.author.server_permissions.administrator:
        serv.config.update("gold_id", None)
        await client.send_message(message.channel, "The gold role has been disabled.")
            
    elif message.content.lower().startswith(".config platinum ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Platinum", hoist=True)
            serv.config.update("platinum_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new platinum role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("platinum_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new platinum role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable platinum") and message.author.server_permissions.administrator:
        serv.config.update("platinum_id", None)
        await client.send_message(message.channel, "The platinum role has been disabled.")
            
    elif message.content.lower().startswith(".config diamond ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Diamond", hoist=True)
            serv.config.update("diamond_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new diamond role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("diamond_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new diamond role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable diamond") and message.author.server_permissions.administrator:
        serv.config.update("diamond_id", None)
        await client.send_message(message.channel, "The diamond role has been disabled.")
            
    elif message.content.lower().startswith(".config master ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Master", hoist=True)
            serv.config.update("master_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new master role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("master_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new master role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable master") and message.author.server_permissions.administrator:
        serv.config.update("master_id", None)
        await client.send_message(message.channel, "The master role has been disabled.")
            
    elif message.content.lower().startswith(".config grandmaster ") and message.author.server_permissions.administrator:
        if len(message.role_mentions) == 0:
            role = await client.create_role(message.author.server, name="Grandmaster", hoist=True)
            serv.config.update("grandmaster_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new grandmaster role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            serv.config.update("grandmaster_id", role.id)
            await client.send_message(message.channel, "Config Updated! Your new grandmaster role is **{0}**".format(message.role.mention))
        elif len(message.role_mentions) > 1:
            await client.send_message(message.channel, "You mentioned too many roles in this command! Please try again using only one.")

    elif message.content.lower().startswith(".config disable grandmaster") and message.author.server_permissions.administrator:
        serv.config.update("grandmaster_id", None)
        await client.send_message(message.channel, "The grandmaster role has been disabled.")
            
    elif message.content.lower().startswith(".config") and message.author.server_permissions.administrator:
        config = serv.config.load()
        embed=discord.Embed()
        embed=discord.Embed(title="Ow Bot Config", description="Configuration for the OW Role Bot")
        embed.add_field(name="Role", value="** **", inline=True)
        embed.add_field(name="{0}".format(config["role"].title()), value="** **", inline=True)
        embed.set_footer(text="Made by u/TheTimebike")
        await client.send_message(message.channel, embed=embed)

    elif None not in config["members"].get(message.author.id, [None, None]):
        stats = api.Api().get(api.STATS_ROUTE.format(config["members"][message.author.id][0], config["members"][message.author.id][1]))
        try:
            rank = stats["stats"]["competitive"]["overall_stats"]["{0}_tier".format(config["role"])]
            if rank != None:
                to_remove, ranks = [], ["bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster"]
                for rank_name in ranks:
                    if rank_name.lower() != rank.lower() and config.get("{0}_id".format(rank_name), None) != None:
                        to_remove.append(get_role(message.author.server.roles, id=config["{0}_id".format(rank_name)]))
                for role in to_remove:
                    await client.remove_roles(message.author, role)
                await client.add_roles(message.author, get_role(message.author.server.roles, id=config["{0}_id".format(rank)]))
        except Exception as ex:
            print(ex)
        
        try:
            for role, achievement_block in stats["achievements"].items():
                for achievement, state in achievement_block.items():
                    if state == True and config.get(achievement, None) != None:
                        await client.add_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))
                    if state == False and config.get(achievement, None) != None:
                        await client.remove_roles(message.author, get_role(message.author.server.roles, id=config[achievement]))
        except Exception as ex:
            print(ex)

        try:
            for hero, playtime_block in config["time"].items():
                overall_hero_playtime = stats["heroes"]["playtime"]["quickplay"].get(hero, 0) +  stats"heroes"]["playtime"]["competitive"].get(hero, 0)
                for key, attr in playtime_block.items():
                    if int(overall_hero_playtime) >= int(key):
                        await client.add_roles(message.author, get_role(message.author.server.roles, id=attr))
        except Exception as ex:
            print(ex)
client.run(auth.token)
