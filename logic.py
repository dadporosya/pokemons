from random import randint
import requests
from info import *


class Move():
    def __init__(self, name, damage, entry, accuracy, pokemon_attack, lvl):
        self.name = name
        self.damage = damage
        self.entry = entry
        self.accuracy = accuracy
        self.pokemon_attack = pokemon_attack
        self.lvl = lvl

    def use(self):
        if randint(1, 100) <= self.accuracy:
            damage = self.damage * self.pokemon_attack / 100
        else:
            damage = 0
        return {
            "entry": self.entry,
            "damage": damage
        }


class Pokemon:
    pokemons = {}
    max_defense = 95

    # Инициализация объекта (конструктор)
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="default", front=True, shiny=False, level=1, exp=0,
                 json_name=None):

        self.pokemon_trainer = pokemon_trainer
        #
        self.pokemon_number = pokemon_number
        self.url = "https://pokeapi.co/api/v2/pokemon/"
        self.pokemon_url = self.url + str(self.pokemon_number)

        self.front = front
        self.shiny = shiny

        self.possible_orientations = ["back", "front"]
        self.possible_shiny = ["default", "shiny"]

        self.start_attack, self.start_hp, self.start_defense, self.height, self.weight = self.get_stats()
        self.hp = self.start_hp
        self.attack = self.start_attack
        self.defense = self.start_defense

        self.img = self.get_img()
        if not json_name:
            self.name = self.get_name()
        else:
            self.name = json_name
        self.ability = self.get_ability()
        self.abilities = []
        for ability in self.ability:
            self.abilities.append(ability["ability"]["name"])

        self.moves_raw = self.get_moves()
        self.moves = []

        if level <= 0:
            level = 1
        self.level = level
        self.exp = exp
        self.feed(start=True)

        self.type = pokemon_type

        self.json_name = json_name

        Pokemon.pokemons[pokemon_trainer] = self

    def feed(self, start=False):
        old_stats = {
            "level": self.level,
            "attack": self.attack,
            "defense": self.defense,
            "hp": self.hp,
            "new abilities": ""
        }
        while self.exp >= (self.level + 1) * 10:
            self.level += 1
            self.exp -= int(self.level * 10)

        new_abilities = []
        if old_stats["level"] != self.level or start:
            self.attack = int(self.start_attack * (1 + (self.level - 1) * 0.2))
            self.hp = int(self.start_hp * (1 + (self.level - 1) * 0.2))
            self.defense = int(self.start_defense * (1 + (self.level - 1) * 0.05))
            if self.defense > Pokemon.max_defense:
                self.defense = Pokemon.max_defense

            if start:
                old_stats["level"] = 0
            for move in self.moves_raw.values():
                if old_stats["level"] < move.lvl <= self.level:
                    self.moves.append(move)
                    new_abilities.append(move.name)

        new_stats = {
            "level": self.level,
            "attack": self.attack,
            "defense": self.defense,
            "hp": self.hp,
            "new abilities": ", ".join(new_abilities)
        }
        return old_stats, new_stats

    # Метод для получения картинки покемона через API
    def get_stats(self):
        response = requests.get(self.pokemon_url)
        if response.status_code == 200:
            data = response.json()
            attack = data["stats"][1]["base_stat"]
            hp = data["stats"][0]["base_stat"]
            defense = data["stats"][2]["base_stat"]

            height = data["height"]
            weight = data["weight"]
            return attack, hp, defense, height, weight
        else:
            return 0, 0, 0

    def get_img(self):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon-form/{self.pokemon_number}")
        if response.status_code == 200:
            data = response.json()
            img_front_url = data['sprites'][
                f'{self.possible_orientations[self.front]}_{self.possible_shiny[self.shiny]}']
            return img_front_url
        else:
            return "https://demofree.sirv.com/nope-not-here.jpg"

    def turn(self):
        self.front = not self.front
        self.img = self.get_img()

    def shine(self):
        self.shiny = not self.shiny
        self.img = self.get_img()

    # Метод для получения имени покемона через API
    def get_name(self):
        response = requests.get(self.pokemon_url)
        if response.status_code == 200:
            data = response.json()
            return (data['forms'][0]['name'])
        else:
            return "Pikachu"

    def get_ability(self):
        response = requests.get(self.pokemon_url)
        if response.status_code == 200:
            data = response.json()
            abilities = data["abilities"]
            return abilities
        else:
            return [{
                "ability": {
                    "name": None,
                    "url": None
                },
                "is_hidden": True,
                "slot": None
            }]

    def get_moves(self):
        response = requests.get(self.pokemon_url)
        moves = {"pass": Move("pass", 0, "You've passed", 0, 0, 1)}
        if response.status_code == 200:
            data = response.json()
            raw_moves = data["moves"]
            i = -1
            for move_dict in raw_moves:
                i += 1

                move = move_dict["move"]
                move_url = move["url"]
                name = move["name"]
                move_response = requests.get(move_url)
                if move_response.status_code == 200:
                    move_data = move_response.json()
                    damage = move_data["power"]
                    if not damage or damage == "null":
                        damage = 0
                        continue

                    accuracy = move_data["accuracy"]
                    if not accuracy or accuracy == "null":
                        accuracy = 0
                    try:
                        entry = move_data["effect_entries"][0]["effect"]
                    except:
                        entry = "Nothing happens..."
                    if not accuracy or accuracy == "null":
                        entry = "Nothing happens..."

                    lvl = move_dict["version_group_details"][0]["level_learned_at"] + 1

                else:
                    damage = 0
                    accuracy = 0
                    entry = "Nothing happens..."
                    lvl = 1

                moves[name] = Move(name, damage, entry, accuracy, self.attack, lvl)

        return moves

    def show_abilities(self):
        return self.abilities

    def show_moves(self):
        return self.moves

    def take_damage(self, damage, enemy_type=None):
        self.hp -= damage * (1 - self.defense / 100)
        print("attack", damage, 1 - self.defense / 100)
        if self.hp < 0:
            self.hp = 0
        return self.hp

    # Метод класса для получения информации
    def info(self):
        message = (f"Имя покемона: {self.name}\n"
                   f"Тип: {self.type}\n"
                   f"W: {self.weight}\n"
                   f"H: {self.height}\n"
                   f"Статы твоего покемона:\n"
                   f"Атака: {self.attack}\n"
                   f"Защита: {self.defense}\n"
                   f"Здоровье: {self.hp}\n"

                   f"Уровень: {self.level}\n"
                   f"Опыт: {self.exp}\n"
                   
                   f"Json_name: {self.json_name}\n"

                   f"Способности твоего покемона: ")
        for ab in self.moves:
            message += ab.name + ", "
        message = message[:-2]
        # f"Способности твоего покемона: {[print(ab, end="") for ab in self.show_abilities()]}"
        return message

    # Метод класса для получения картинки покемона
    def show_img(self):
        return self.img

    def deal_damage(self, move, enemy_type=None):
        use = move.use()
        print(use)
        use["damage"] += self.bonus_dmg(use["damage"], enemy_type)

        return use

    def bonus_dmg(self, dmg, enemy_type=None):
        sum_dmg = 0
        return sum_dmg


class Constructor:
    def __init__(self, pokemon_trainer, shiny=False, level=1, exp=0, type=None, pokemon_number=None, json_name=None):
        self.pokemon_trainer = pokemon_trainer

        if pokemon_number:
            self.pokemon_number = pokemon_number
        else:
            self.pokemon_number = randint(1, 1000)

        self.url = "https://pokeapi.co/api/v2/pokemon/"
        self.pokemon_url = self.url + str(self.pokemon_number)



        self.shiny = shiny
        self.level = level
        self.exp = exp

        self.attributes = {
            "weight": "normal",
            "height": "normal"
        }

        if json_name:
            self.name = json_name

        if not type:
            self.weight, self.height = self.get_w_h()

            if self.weight > weights["avr"] * 2:
                self.attributes["weight"] = "heavy"
            elif self.weight < weights["avr"] / 2:
                self.attributes["weight"] = "light"

            if self.height > heights["avr"] * 2:
                self.attributes["height"] = "tall"
            elif self.height < heights["avr"] / 2:
                self.attributes["height"] = "small"

            print(self.attributes)

        if (self.attributes["weight"] == "heavy" and self.attributes["height"] == "tall") or type == "big":
            Big(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        elif (self.attributes["weight"] == "light" and self.attributes["height"] == "small") or type == "tiny":
            Tiny(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        elif self.attributes["weight"] == "light" or type == "light":
            Light(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        elif self.attributes["weight"] == "heavy" or type == "heavy":
            Heavy(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        elif self.attributes["height"] == "tall" or type == "tall":
            Tall(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        elif self.attributes["height"] == "small" or type == "small":
            Small(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)
        else:
            Pokemon(self.pokemon_trainer, self.pokemon_number, shiny=self.shiny, level=self.level, exp=self.exp, json_name=json_name)

    def get_w_h(self):
        response = requests.get(self.pokemon_url)
        if response.status_code == 200:
            data = response.json()
            weight = data["weight"]
            height = data["height"]
            print(f"w: {weight}, h: {height}")
            return weight, height
        else:
            return 0, 0


class Heavy(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="heavy", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type=pokemon_type, front=front, shiny=shiny,
                         level=level, exp=exp, json_name=json_name)

        self.start_hp *= 1.5
        self.skill = 1

        # print(self.type)

    def bonus_dmg(self, dmg, enemy_type=None):
        print("heavy")
        bonus = 0
        if enemy_type in ["light", "tiny"]:
            bonus = [0, dmg * 0.5][randint(1, 10) <= self.skill]
        print("heavy", bonus)
        return bonus


class Tall(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="tall", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type=pokemon_type, front=front, shiny=shiny,
                         level=level, exp=exp, json_name=json_name)

        self.start_attack *= 1.5
        self.skill = 1

        # print(self.type)

    def bonus_dmg(self, dmg, enemy_type=None):
        bonus = 0
        if enemy_type in ["small", "tiny"]:
            bonus = [0, dmg * 0.5][randint(1, 10) <= self.skill]
        print("tall", bonus)
        return bonus


class Big(Heavy, Tall):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="big", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type=pokemon_type, front=front, shiny=shiny,
                         level=level, exp=exp, json_name=json_name)

        self.skill = 1
        # print(self.type)

    def bonus_dmg(self, dmg, enemy_type=None):
        bonus = 0
        for base in Big.__bases__:
            bonus += base.bonus_dmg(self, dmg, enemy_type)

        return bonus


class Light(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="light", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type=pokemon_type, front=front, shiny=shiny,
                         level=level, exp=exp, json_name=json_name)

        self.agility = 1

    def take_damage(self, damage, enemy_type=None):
        print("light")
        damage = [damage, 0][randint(1, 10) <= self.agility]
        if damage == 0:
            print("light: miss")
        super().take_damage(damage)


class Small(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="small", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type=pokemon_type, front=front, shiny=shiny,
                         level=level, exp=exp, json_name=json_name)

    def take_damage(self, damage, enemy_type=None):
        print("small")
        if enemy_type in ["tall", "big"]:
            damage = [damage, 0][randint(1, 10) <= 1]
        if damage == 0:
            print("small: miss")
        super().take_damage(damage)


class Tiny(Light, Small):
    def __init__(self, pokemon_trainer, pokemon_number, pokemon_type="tiny", front=True, shiny=False, level=1, exp=0, json_name=None):
        super().__init__(pokemon_trainer, pokemon_number, pokemon_type, front=front, shiny=shiny, level=level, exp=exp, json_name=json_name)

    # def take_damage(self, damage, enemy_type=None):
    #     super().take_damage(damage, enemy_type=enemy_type)
