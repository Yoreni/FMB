#from fmb import Monster, Player
import sqlite3
import random
#from logic import Player, Monster

# making a connection to the data base
with sqlite3.connect("monsters.db") as database_connection:
    cursor = database_connection.cursor()

class Player:
    def __init__(self, _id, nuggets):
        self.nuggets = nuggets
        self._id = _id

    def get_monsters(self, alive = None):
        # getting the players monsters
        if alive is None:
            command = "SELECT id FROM beasts WHERE owner_id = {}"
        else:
            command = "SELECT id FROM beasts WHERE owner_id = {} AND alive = " + str(alive)
        cursor.execute(command.format(self._id))
        beast_answer = cursor.fetchall()

        monsters = []
        for i in beast_answer:
            monster = Monster.load(i[0])  # [0] cos the id is in the tuple
            monsters.append(monster)

        return monsters

    def get_id(self):
        return self._id

    @staticmethod
    def create_profile(id):
        command = "INSERT INTO players VALUES ({}, 7500)"
        cursor.execute(command.format(id))
        database_connection.commit()

        return Player.load(id)

    @staticmethod
    def load(id):
        command = "SELECT * FROM players WHERE id = {}"
        cursor.execute(command.format(id))
        player_answer = cursor.fetchall()
        if len(player_answer) == 0:
            return None
        player_answer = player_answer[0]   # [0] cos it will return it as a list

        player = Player(id, player_answer[1])
        return player

class Monster:
    def __init__(self, stat1, stat2, stat3, stat4, monster_id: int, alive: bool,owner=None):
        self.stat1 = stat1
        self.stat2 = stat2
        self.stat3 = stat3
        self.stat4 = stat4
        self.alive = alive
        self.owner = owner
        self.monster_id = monster_id

    def __str__(self):
        output = f"Stat1: {self.stat1} Stat2: {self.stat2} Stat3: {self.stat3} Start4: {self.stat4} POWER: {self.get_power()}"
        return output

    def get_power(self):
        return self.stat1 + self.stat2 + self.stat3 + self.stat4

    def get_stat1(self):
        return self.stat1

    def get_stat2(self):
        return self.stat2

    def get_stat3(self):
        return self.stat3

    def get_stat4(self):
        return self.stat4

    def get_tier(self):
        if self.get_power() < 1000:
            return 1
        elif self.get_power() < 2500:
            return 2
        else:
            return 3

    def change_owner(self, new_owner):
        self.owner = new_owner

    def get_owner(self):
        return self.owner

    def get_odds(self, other_monster):
        return self.get_power() / (self.get_power() + other_monster.get_power())

    def eat(self, other_monster):
        #if other_monster.alive:
        self.stat1 += other_monster.get_stat1()
        self.stat2 += other_monster.get_stat2()
        self.stat3 += other_monster.get_stat3()
        self.stat4 += other_monster.get_stat4()
        other_monster.alive = False

    def get_id(self):
        return self.monster_id

    #making a new monster from scratch
    @staticmethod
    def grow():
        stat1 = random.randint(10, 100)
        stat2 = random.randint(10, 100)
        stat3 = random.randint(10, 100)
        stat4 = random.randint(10, 100)

        # adding the moster to the data base
        command = "INSERT INTO beasts (owner_id, stat1, stat2, stat3, stat4) VALUES({},{},{},{},{})"
        cursor.execute(command.format("0", stat1, stat2, stat3, stat4))
        database_connection.commit()

        # we dont know the id of the monster we just added so now we are going to get that
        cursor.execute("SELECT id FROM beasts ORDER BY id DESC LIMIT 0,1")
        answer = cursor.fetchall()
        id = answer[0][0]

        return Monster(stat1, stat2, stat3, stat4, id, True)

    # this gets a monster from the database
    @staticmethod
    def load(monster_id):
        try:
            command = "SELECT * FROM beasts WHERE id = {}"
            cursor.execute(command.format(monster_id))
            answer = cursor.fetchall()
            if len(answer) == 0:
                return None
            answer = answer[0]  # [0] cos it will return it as a list
            alive = True if answer[6] == 1 else False

            beast = Monster(answer[2], answer[3], answer[4], answer[5], monster_id, alive, Player.load(str(answer[1])))
            return beast
        except IndexError:
            print("Error: tried acessing beast id", id, "but it doesnt exist")
            return None

    @staticmethod
    def fight(battle_request):
        challgeners_beast = battle_request.challengers_beast
        oponents_beast = battle_request.opponents_beast

        # calculating the odds and who will win
        odds = round(oponents_beast.get_odds(challgeners_beast) * 100)

        action_done = ""
        if random.randint(0, 100) < odds:
            if battle_request.opponents_action == "eat":
                oponents_beast.eat(challgeners_beast)
            elif battle_request.opponents_action == "collect":
                challgeners_beast.change_owner(oponents_beast.owner)
            winner = "oponent"
            action_done = battle_request.opponents_action
        else:
            if battle_request.challengers_action == "eat":
                challgeners_beast.eat(oponents_beast)
            elif battle_request.challengers_action == "collect":
                oponents_beast.change_owner(challgeners_beast.owner)
            winner = "challanger"
            action_done = battle_request.challengers_action

        oponents_beast.save()
        challgeners_beast.save()

        return (winner, action_done)
    # this saves the monster to the data base
    def save(self):
        owner_id = self.owner.get_id() if self.owner is not None else "0"
        alive = 1 if self.alive else 0

        command = "UPDATE beasts SET stat1 = {}, stat2 = {}, stat3 = {}, stat4 = {}, owner_id = {}, alive = {} WHERE id = {}"
        cursor.execute(command.format(self.stat1, self.stat2, self.stat3, self.stat4, owner_id, alive, self.monster_id))
        database_connection.commit()
