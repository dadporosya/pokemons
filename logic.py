from random import randint
import requests

class Pokemon:
    pokemons = {}
    # Инициализация объекта (конструктор)
    def __init__(self, pokemon_trainer, front=True, shiny=False):

        self.pokemon_trainer = pokemon_trainer

        self.pokemon_number = randint(1, 1000)
        self.url = "https://pokeapi.co/api/v2/pokemon/"
        self.pokemon_url = self.url + str(self.pokemon_number)

        self.front = front
        self.shiny = shiny

        self.possible_orientations = ["back", "front"]
        self.possible_shiny = ["default", "shiny"]


        self.img = self.get_img()
        self.name = self.get_name()
        self.ability = self.get_ability()

        Pokemon.pokemons[pokemon_trainer] = self

    # Метод для получения картинки покемона через API
    def get_img(self):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon-form/{self.pokemon_number}")
        if response.status_code == 200:
            data = response.json()
            img_front_url = data['sprites'][f'{self.possible_orientations[self.front]}_{self.possible_shiny[self.shiny]}']
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

    def show_abilities(self):
        abilities = []
        for ability in self.ability:
            abilities.append(ability["ability"]["name"])
        return abilities



    # Метод класса для получения информации
    def info(self):
        message = (f"Имя твоего покемона: {self.name}\n"
                   f"Способности твоего покемона: ")
        for ab in self.show_abilities():
            message += ab + ", "
        message = message[:-2]
            #f"Способности твоего покемона: {[print(ab, end="") for ab in self.show_abilities()]}"
        return message

    # Метод класса для получения картинки покемона
    def show_img(self):
        return self.img



