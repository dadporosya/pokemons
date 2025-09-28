import telebot
from config import token

from logic import Pokemon, Constructor

from random import choice, randint

import json

bot = telebot.TeleBot(token)
bot.remove_webhook()

battle = False
enemy = None


# your_turn = True

class Battle:
    battle = False


class CreatingPokemon:
    creating_pokemon = False


def choose_pokemon(message, data, text):
    user_id = str(message.from_user.id)
    CreatingPokemon.creating_pokemon = True
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = [telebot.types.KeyboardButton(f"{key} lvl: {data[user_id][key]["level"]}") for key in list(data[user_id].keys())]
    markup.add(*btns)
    bot.send_message(message.chat.id,
                     text,
                     reply_markup=markup)

@bot.message_handler(commands=['changePokemon'])
def change_pokemon(message):
    with open("data.json", "r") as file:
        data = json.load(file)
    choose_pokemon(message, data, "Choose new pokemon")

@bot.message_handler(commands=['changeName'])
def change_name(message):
    user_id = message.from_user.id
    if message.from_user.id in Pokemon.pokemons.keys():
        pokemon =  Pokemon.pokemons[user_id]
        with open("data.json", "r" , encoding="utf-8") as file:
            data = json.load(file)
        new_name = telebot.util.extract_arguments(message.text)
        if new_name in list(data[str(user_id)].keys()):
            bot.reply_to(message, "You already have a pokemon with such name")
        else:
            old_json_name = pokemon.json_name
            print(old_json_name)
            old_data = data[str(user_id)][old_json_name]
            del data[str(user_id)][old_json_name]
            pokemon.json_name = new_name
            data[str(user_id)][new_name] = old_data

            Pokemon.pokemons[user_id].name = new_name
            Pokemon.pokemons[user_id].json_name = new_name

            save(pokemon, user_id)

            with open("data.json", "w") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            
    else:
        bot.reply_to(message, "You do not have any pokemons! Use cmd '/go' to create a new one!")


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        del Pokemon.pokemons[message.from_user.id]
    with open("data.json", "r") as file:
        data = json.load(file)
    user_id = message.from_user.id
    if str(user_id) in list(data.keys()):
        choose_pokemon(message, data,
                       "You can choose one of the already created pokemons, or make a new one using '/go' command")
    else:
        bot.reply_to(message, "Hello! Use cmd '/go' to create new pokemon!")


def load(message, pdata):
    Constructor(message.from_user.id, level=pdata["level"], exp=pdata["exp"], type=pdata["type"], pokemon_number=pdata["pokemon_number"], json_name=pdata["json_name"])
    pokemon = Pokemon.pokemons[message.from_user.id]
    bot.send_message(message.chat.id, pokemon.info())
    bot.send_photo(message.chat.id, pokemon.show_img())


def save(pokemon, user_id):
    user_id = str(user_id)
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    info = {
        "pokemon_number": pokemon.pokemon_number,
        "level": pokemon.level,
        "exp": pokemon.exp,
        "type": pokemon.type,
        "json_name": pokemon.json_name
    }

    if user_id not in list(data.keys()):
        data[user_id] = {}

    if not pokemon.json_name:
        counter = 0
        for key in list(data[user_id].keys()):
            if pokemon.name in key:
                counter += 1
        pokemon.json_name = pokemon.name + str(counter)
        info["json_name"] = pokemon.json_name

    data[user_id][pokemon.json_name] = info

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.id not in Pokemon.pokemons.keys():
        bot.send_message(message.chat.id, "Creating pokemon...")
        Constructor(message.from_user.id)
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())

        save(pokemon, message.from_user.id)

    else:
        bot.reply_to(message, "Ты уже создал себе покемона")


@bot.message_handler(commands=['info'])
def info(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "You do not have a pokemon! Use cmd /go to create new one!")


@bot.message_handler(commands=['turn'])
def turn(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        Pokemon.pokemons[message.from_user.id].turn()
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.reply_to(message,
                     f"Your pokemon orientation has been changed to {pokemon.possible_orientations[pokemon.front]}")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "You do not have any pokemon. Use '/go' to create one!")


@bot.message_handler(commands=['shine'])
def shine(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        Pokemon.pokemons[message.from_user.id].shine()
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.reply_to(message, f"Your pokemon is {pokemon.possible_shiny[pokemon.shiny]} now!")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "You do not have any pokemon. Use '/go' to create one!")


def create_btns_for_moves(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = []
    for move in Pokemon.pokemons[message.from_user.id].moves:
        btns.append(telebot.types.KeyboardButton(move.name))
    markup.add(*btns)

    bot.send_message(message.chat.id, "Choose your move", reply_markup=markup)


@bot.message_handler(commands=['battle'])
def battle(message):
    battle = Battle.battle
    if not battle:
        Battle.battle = True
        bot.reply_to(message, f"BATTLE starts!!!")
        Constructor("ENEMY", shiny=choice([True, False]),
                    level=Pokemon.pokemons[message.from_user.id].level + randint(-1, 2))
        pokemon = Pokemon.pokemons["ENEMY"]

        # pokemon = Pokemon("ENEMY", shiny=choice([True, False]),
        #                   level=Pokemon.pokemons[message.from_user.id].level + randint(-1, 2))

        bot.send_message(message.chat.id, "YOUR ENEMY IS...")
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())

        create_btns_for_moves(message)
    else:
        bot.reply_to(message, f"BATTLE has already been started!")


def win(message):
    if Battle.battle:
        bot.send_message(message.chat.id, f"YOU WIN!")
        Battle.battle = False

        exp = Pokemon.pokemons["ENEMY"].level * 10 + randint(Pokemon.pokemons["ENEMY"].level * -5,
                                                             Pokemon.pokemons["ENEMY"].level * 5)
        bot.send_message(message.chat.id, f"You have earned {exp} exp!")

        Pokemon.pokemons[message.from_user.id].exp += exp

        save(Pokemon.pokemons[message.from_user.id], message.from_user.id)

    # exp and level


@bot.message_handler(commands=['win'])
def auto_win(message):
    win(message)


@bot.message_handler(commands=['feed'])
def feed(message):
    old, new = Pokemon.pokemons[message.from_user.id].feed()
    if old["level"] != new["level"]:
        text = [f"{key}: {old[key]} -> {new[key]}\n" for key in old.keys()]
        bot.send_message(message.chat.id, " ".join(text))

        save(Pokemon.pokemons[message.from_user.id], message.from_user.id)
    else:
        bot.send_message(message.chat.id,
                         f"You must have at least {(Pokemon.pokemons[message.from_user.id].level + 1) * 10} to feed your pokemon!")


@bot.message_handler(commands=['end'])
def battle_end(message):
    if Battle.battle:
        bot.send_message(message.chat.id, f"Battle end")
        Battle.battle = False


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    if CreatingPokemon.creating_pokemon:
        with open("data.json", "r") as file:
            data = json.load(file)
        for key in list(data[str(user_id)].keys()):
            if key in message.text:
                load(message, data[str(user_id)][key])
                break
        return

    user_pokemon = Pokemon.pokemons[message.from_user.id]

    if message.text in user_pokemon.moves_raw.keys():
        move = message.text
    else:
        move = None
    battle = Battle.battle
    if battle:
        enemy = Pokemon.pokemons["ENEMY"]
        use = user_pokemon.deal_damage(user_pokemon.moves_raw[move], enemy.type)
        dealt_damage = int(use["damage"] * (1 - enemy.defense / 100))
        bot.reply_to(message, use["entry"])
        bot.send_message(message.chat.id, f"You have dealt {dealt_damage} damage")
        Pokemon.pokemons["ENEMY"].take_damage(dealt_damage)

        bot.send_message(message.chat.id, f"Enemy hp: {Pokemon.pokemons["ENEMY"].hp}")

        if Pokemon.pokemons["ENEMY"].hp <= 0:
            win(message)
            # exp and level
        else:
            enemy_move = choice(enemy.moves)
            bot.send_message(message.chat.id, f"Enemy's move: {enemy_move.name}")
            use = enemy.deal_damage(enemy_move, user_pokemon.type)

            bot.send_message(message.chat.id, use["entry"])
            dealt_damage = int(use["damage"] * (1 - user_pokemon.defense / 100))
            Pokemon.pokemons[message.from_user.id].take_damage(dealt_damage, enemy.type)

            bot.send_message(message.chat.id, f"Enemy has dealt {dealt_damage} damage")

            bot.send_message(message.chat.id, f"Your hp: {Pokemon.pokemons[message.from_user.id].hp}")

            if Pokemon.pokemons[message.from_user.id].hp <= 0:
                bot.send_message(message.chat.id, f"YOU LOSE! :(((((")
                Pokemon.pokemons[message.from_user.id].hp = Pokemon.pokemons[message.from_user.id].start_hp
                Battle.battle = False
                return

            create_btns_for_moves(message)

    else:
        if move:
            bot.reply_to(message, f"{move}:\n"
                                  f"Damage: {user_pokemon.moves_raw[move].damage}\n"
                                  f"Accuracy: {user_pokemon.moves_raw[move].accuracy}\n")


bot.infinity_polling(none_stop=True)
