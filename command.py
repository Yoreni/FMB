from logic import Player
from requests import Query, BattleRequest
from utils import get_beasts_by_power, calc_max_page, validate_int, splice_monsters, display_monsters, \
    get_beasts_by_comparison, get_user


# args in format !fmb profile <user> (page)
# prints a users monsters
async def print_users_monsters(bot, args, channel):
    # getting the users and also checking if the user is valid
    a = await get_user(bot, args[2], channel.guild)
    if a is None:
        await channel.send("That is not a valid user")
        return
    user = Player.load(str(a.id))
    if user is None:
        await channel.send("That user does not have a profile")
        return

    # getting the users beats and sorting it so it always displays the most powerful beasts first
    beasts = get_beasts_by_power(user)

    # getting the page
    # if the user does not specify a page then we set it to its defuault (1)
    max_page = calc_max_page(beasts)
    if len(args) <= 3:
        page = 1
    else:
        # else we will try to parse the number the user has typed
        page = int(args[3]) if validate_int(args[3], min=1, max=max_page) else 1
    beasts = splice_monsters(beasts, page)

    output_message = await display_monsters(channel, beasts, page, max_page)

    # editing the users command so we save code if the user wants to switch pages by reacting
    if len(args) <= 3:
        args.append(str(page))
    else:
        args[3] = str(page)
    q = Query(args, output_message)
    if q not in bot.queries:
        bot.queries.append(q)
    return q


#not really a command but this shows the screen were the player can choose his monster to fight
async def print_choose_monsters(bot, battle_request, channel):
    beasts = get_beasts_by_comparison(battle_request.challenger, battle_request.opponents_beast)

    max_page = calc_max_page(beasts)
    page = int(battle_request.command[3])
    beasts = splice_monsters(beasts, page)

    prepend = f"**Beast fighting against** \n{str(battle_request.opponents_beast)} \n \n"
    output_message = await display_monsters(
        channel, beasts, page, max_page, prepend=prepend)

    battle_request.command[3] = str(page)
    battle_request.message = output_message

    return battle_request