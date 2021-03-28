import discord


# this will be how the bot remember which users did command which will be used for example when a player reacts
# to a bot message asking the bot to do something else
class Query:
    # command is the command args that the user typed
    # message is the output message from the bot
    def __init__(self, command, message: discord.Message):
        self.message = message
        self.command = command

    def get_message(self):
        return self.message

    def get_command(self):
        return self.command


class BattleRequest(Query):
    def __init__(self, command, message: discord.Message, opponents_beast, challenger):
        super(BattleRequest, self).__init__(command, message)
        self.opponents_beast = opponents_beast
        self.challenger = challenger
        self.challengers_beast = None
        # these atrubute decided wether if a battle is won you eat or collect
        self.challengers_action = None
        self.opponents_action = None

        self.opponent_has_accepted = False
