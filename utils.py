import math
import re

BEASTS_PER_PAGE = 6
EMOJI_DISPLAY = \
    ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


# this validates an int and checks if its in the right range if a string
# gets passed into number then it will try to treat it as a string
def validate_int(number, **kwargs):
    kwargs.setdefault("min", -math.inf)
    kwargs.setdefault("max", math.inf)

    # if its an str we try to convert it as an int
    if type(number) is str:
        if number.isnumeric():
            number = int(number)
        else:
            return False

    if kwargs["min"] <= number <= kwargs["max"]:
        return True
    else:
        return False


# returns the number of pages needed to print the list of monsters
def calc_max_page(monsters):
    return math.ceil(len(monsters) / BEASTS_PER_PAGE)


#  takes a list of monsters and returns the a smaller list of you can display them easier
def splice_monsters(monsters, page):
    # making sure we are looking at a page in bounds
    max_page = calc_max_page(monsters)
    if not validate_int(page, min=1, max=max_page):
        raise ValueError

    monsters = monsters[BEASTS_PER_PAGE * (page - 1): BEASTS_PER_PAGE * page]
    return monsters


def get_beasts_by_power(player):
    # True cos we only want to show alive ones
    beasts = player.get_monsters(True)
    beasts.sort(key=lambda beast: beast.get_power(), reverse=True)
    return beasts

#this gets the plyers beasts in order of differnce of the comparing beast
def get_beasts_by_comparison(player, comparing_beast):
    # True cos we only want to show alive ones
    beasts = player.get_monsters(True)
    beasts.sort(key=lambda beast: abs(comparing_beast.get_power() - beast.get_power()), reverse=False)
    return beasts

# gets a user from a ping
async def get_user(bot, ping_string, server):
    #if its at at form
    if re.match("<@![0-9]{17,23}>", ping_string):
        # get rid of everying thing we dont want with a regex expression
        ping_string = re.sub(r"[^0-9]", "", ping_string)
    #if its just the raw id
    elif validate_int(ping_string):
        ping_string = int(ping_string)
    #else we will if its someones user name in the server
    else:
        #server = bot.get_guild(guild_id)
        members = await server.query_members(query=ping_string, limit=5)
        if len(members) == 0:
            return None
        else:
            member = members[0]  # get the first one

        ping_string = member.id
    return await bot.fetch_user(ping_string)

# prints a list of monsters to discord
async def display_monsters(channel, beasts, page: int, max_page: int, **kwargs):
    # this option is here if you want to add text after or before
    prepend = kwargs.setdefault("prepend", "")
    append = kwargs.setdefault("append", "")

    output = ""
    output += "Page " + str(page) + "\n"
    for count, beast in enumerate(beasts):
        output += EMOJI_DISPLAY[count] + " " + str(beast) + "\n \n"
    output = prepend + output + append
    output_message = await channel.send(output)

    # adding the emjois so users can get to the other pages easily
    if page > 1:
        await output_message.add_reaction("⬅")
    if page < max_page:
        await output_message.add_reaction("➡")

    # adding these options so you can do things to speficic monsters
    for j in range(count + 1):
        await output_message.add_reaction(EMOJI_DISPLAY[j])

    return output_message
