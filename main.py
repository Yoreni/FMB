import random
import discord
import json
import re
import math
import sqlite3

from logic import Player, Monster
from utils import *
from requests import Query, BattleRequest
from command import print_users_monsters, print_choose_monsters

BOT_COMMAND_PREFIX = "!fmb"

# interaction with discord
class MyClient(discord.Client):
    # displays the outcome of a beast fight
    async def display_fight(self, battle_request):
        challgeners_beast = battle_request.challengers_beast
        oponents_beast = battle_request.opponents_beast
        channel = battle_request.message.channel

        # calculating the odds and who will win
        odds = round(oponents_beast.get_odds(challgeners_beast) * 100)

        output = ""

        output += str(oponents_beast)
        output += " **" + str(odds) + "% chance of wining**"
        output += "\n VS \n"

        output += str(challgeners_beast)
        output += " **" + str(100 - odds) + "% chance of wining**\n \n"

        winner, action = Monster.fight(battle_request)

        if action == "eat":
            output += "Winner has eaten the losers monster\n"
        elif action == "collect":
            output += "Winner has collected the losers monster\n"

        if winner == "oponent":
            output += f"<@!{oponents_beast.get_owner().get_id()}>s beast won"
        elif winner == "challanger":
            output += f"<@!{challgeners_beast.get_owner().get_id()}>s beast won"

        output_message = await channel.send(output)
        return output_message

    async def on_ready(self):
        self.queries = []
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # making sure the bot recinises the command even if the user put in too many spaces
        args = re.sub(" +", " ", message.content)
        args = args.split(" ")

        if args[0] == BOT_COMMAND_PREFIX:
            # !fmb profile <user> (page)
            if args[1] == "profile":
                query = await print_users_monsters(self, args, message.channel)
            elif args[1] == "createprofile":
                try:
                    player = Player.create_profile(str(message.author.id))
                    await message.channel.send("Your profile has been created get monsters with `!fmb grow`")
                except sqlite3.IntegrityError:
                    await message.channel.send("You already have a profile")
            elif args[1] == "grow":
                player = Player.load(str(message.author.id))
                beast = Monster.grow()
                beast.change_owner(player)
                beast.save()
                await message.channel.send("You have grown a monster \n" + str(beast))

    async def on_reaction_add(self, reaction, user):
        # if the reaction was added on a message by a bot and the person who reacted is not a bot
        if (not reaction.message.author.bot or user.bot):
            return
        # getting the qurey
        qurey = list(filter(lambda q: q.get_message() == reaction.message, self.queries))
        if(len(qurey) == 0):
            return
        qurey = qurey[0]

        if type(qurey) is BattleRequest:
            # checking that only the person who requested the battle can change like what monster he wants to use
            if str(user.id) == qurey.challenger._id:
                if qurey.challengers_beast is None:
                    page = int(qurey.command[3])
                    if str(reaction) in EMOJI_DISPLAY:
                        #this is getting the challangers beast that he/she selected
                        opponents_beast = qurey.opponents_beast

                        challengers_beasts = get_beasts_by_comparison(qurey.challenger, opponents_beast)
                        challengers_beast = challengers_beasts[((page - 1) * 6) + EMOJI_DISPLAY.index(str(reaction))]
                        qurey.challengers_beast = challengers_beast

                        #ask the user about eating and collecting
                        request_status = ""
                        request_status += "**Oponents Monster** \n"
                        request_status += str(qurey.opponents_beast) + "\n"
                        request_status += "**Your Monster** \n"
                        request_status += str(qurey.challengers_beast) + "\n \n"
                        request_status += "If you win would you like to 🍩eat or 📥collect your opponents beast"

                        #send the message
                        output_message = await reaction.message.channel.send(request_status)
                        await output_message.add_reaction("🍩")
                        await output_message.add_reaction("📥")

                        qurey.message = output_message
                    elif str(reaction) == "⬅" or str(reaction) == "➡":
                        # tweaking the page based on the reaction
                        if str(reaction) == "⬅":
                            page -= 1
                        elif str(reaction) == "➡":
                            page += 1
                        qurey.command[3] = str(page)

                        qurey = await print_choose_monsters(self, qurey, reaction.message.channel)
                elif qurey.challengers_action is None:
                    if str(reaction) == "🍩":
                        qurey.challengers_action = "eat"
                    elif str(reaction) == "📥":
                        qurey.challengers_action = "collect"

                    # now we are going to ask the user to accept the battle request
                    challengers_discord = await self.fetch_user(int(qurey.challenger._id))
                    output = f"<@!{qurey.opponents_beast.owner._id}> {challengers_discord.name} has challanged you to a battle\n\n"
                    output += "**Your Monster**\n" + str(qurey.opponents_beast) + "\n\n"
                    output += "**Oponnents Monster**\n" + str(qurey.challengers_beast) + "\n\n"

                    #output += "React with the green tick to accept this battle."
                    output += "If you win would you like to 🍩eat or 📥collect your opponents beast\n"
                    output += "Ignore this if you dont want to do the battle"

                    output_message = await reaction.message.channel.send(output)
                    qurey.message = output_message
                    await output_message.add_reaction("🍩")
                    await output_message.add_reaction("📥")
                    #await output_message.add_reaction("✅")
                    # await self.display_fight(qurey)
            if  str(user.id) == qurey.opponents_beast.owner._id:
                if qurey.challengers_action is not None:
                    if str(reaction) == "🍩":
                        qurey.opponents_action = "eat"
                    elif str(reaction) == "📥":
                        qurey.opponents_action = "collect"

                    qurey.opponent_has_accepted = True
                    await self.display_fight(qurey)
                   # if str(reaction) == "✅":
                   #     qurey.opponent_has_accepted = True
                   #     await self.display_fight(qurey)
        else:
            args = qurey.get_command()
            if args[0] == BOT_COMMAND_PREFIX:
                if args[1] == "profile":
                    discord_user = await get_user(self, args[2], reaction.message.guild)
                    player = Player.load(str(discord_user.id))
                    page = int(args[3])

                    if str(reaction) == "⬅" or str(reaction) == "➡":
                        # tweaking the pages number depending on the reaction
                        if str(reaction) == "⬅":
                            page -= 1
                        elif str(reaction) == "➡":
                            page += 1
                        args[3] = str(page)

                        query = await print_users_monsters(self, args, reaction.message.channel)
                    elif str(reaction) in EMOJI_DISPLAY:
                        beasts = get_beasts_by_power(player)
                        oponent_beast = beasts[((page - 1) * 6) + EMOJI_DISPLAY.index(str(reaction))]

                        challenger = Player.load(str(user.id))

                        q = BattleRequest(args, None, oponent_beast, challenger)
                        q.command[3] = "1" # this is so it always shows the first page first
                        q = await print_choose_monsters(self, q, reaction.message.channel)
                        self.queries.append(q)

# this inits the bot
def init_bot():
    client = MyClient()
    with open('secret.json', "r") as f:
        data = json.load(f)
    client.run(data["token"])
    return client


if __name__ == '__main__':
    client = init_bot()  # this should be the final line of the if statment cos it wont run any code below it

# See PyCharm help at https://www.jetbrains.com/help/pycharm/