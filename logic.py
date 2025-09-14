from random import randint
import requests

class Move():
    def __init__(self, name, damage, entry, accuracy, pokemon_attack):
        self.name = name
        self.damage = damage
        self.entry = entry
        self.accuracy = accuracy
        self.pokemon_attack = pokemon_attack

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
    # Инициализация объекта (конструктор)
    def __init__(self, pokemon_trainer, front=True, shiny=False, level=1):

        self.pokemon_trainer = pokemon_trainer

        self.pokemon_number = randint(1, 1000)
        self.url = "https://pokeapi.co/api/v2/pokemon/"
        self.pokemon_url = self.url + str(self.pokemon_number)

        self.front = front
        self.shiny = shiny

        self.possible_orientations = ["back", "front"]
        self.possible_shiny = ["default", "shiny"]

        self.start_attack, self.start_hp, self.start_defense = self.get_stats()
        self.hp = self.start_hp
        self.attack = self.start_attack
        self.defense = self.start_defense


        self.img = self.get_img()
        self.name = self.get_name()
        self.ability = self.get_ability()
        self.abilities = []
        for ability in self.ability:
            self.abilities.append(ability["ability"]["name"])

        self.moves_raw = self.get_moves()
        self.moves = []
        for move in self.moves_raw.values():
            self.moves.append(move)

        if level <= 0:
            level = 1
        self.level = level
        self.exp = 0
        self.get_new_lvl()




        Pokemon.pokemons[pokemon_trainer] = self

    def get_new_lvl(self):
        while self.exp >= (self.level+1)*10:
            self.level += 1
            self.exp -= self.level*10
        self.attack = int(self.start_attack*(1 + self.level*0.2))
        self.hp = int(self.start_hp * (1 + self.level * 0.2))
        self.defense = int(self.start_defense * (1 + self.level * 0.2))



    # Метод для получения картинки покемона через API
    def get_stats(self):
        response = requests.get(self.pokemon_url)
        if response.status_code == 200:
            data = response.json()
            attack = data["stats"][1]["base_stat"]
            hp = data["stats"][0]["base_stat"]
            defense = data["stats"][2]["base_stat"]
            return attack,hp,defense
        else:
            return 0,0,0

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
        moves = {"pass": Move("pass", 0, "You've passed", 0, 0)}
        if response.status_code == 200:
            data = response.json()
            raw_moves = data["moves"]
            for move in raw_moves:
                move = move["move"]
                move_url = move["url"]
                name = move["name"]
                move_response = requests.get(move_url)
                if move_response.status_code == 200:
                    move_data = move_response.json()
                    damage = move_data["power"]
                    if not damage or damage == "null":
                        damage = 0

                    accuracy = move_data["accuracy"]
                    if not accuracy or accuracy == "null":
                        accuracy = 0
                    try:
                        entry = move_data["effect_entries"][0]["effect"]
                    except:
                        entry = "Nothing happens..."
                    if not accuracy or accuracy == "null":
                        entry = "Nothing happens..."
                else:
                    damage = 0
                    accuracy = 0
                    entry = "Nothing happens..."

                moves[name] = Move(name, damage, entry,accuracy, self.attack)

        return moves

    def show_abilities(self):
        return self.abilities

    def show_moves(self):
        return self.moves



    # Метод класса для получения информации
    def info(self):
        message = (f"Имя покемона: {self.name}\n"
                   f"Статы твоего покемона:\n"
                   f"Атака: {self.attack}\n"
                   f"Защита: {self.defense}\n"
                   f"Здоровье: {self.hp}\n"
                   f"Уровень: {self.level}\n"
                   f"Опыт: {self.exp}\n"
                   f"Способности твоего покемона: ")
        for ab in self.moves:
            message += ab.name + ", "
        message = message[:-2]
            #f"Способности твоего покемона: {[print(ab, end="") for ab in self.show_abilities()]}"
        return message

    # Метод класса для получения картинки покемона
    def show_img(self):
        return self.img



