import telebot
from config import token

from logic import Pokemon

from random import choice, randint

bot = telebot.TeleBot(token)

battle = False
enemy = None


# your_turn = True

class Battle:
    battle = False


@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.id not in Pokemon.pokemons.keys():
        pokemon = Pokemon(message.from_user.id)
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
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
        bot.reply_to(message, f"BATTLE stars!!!")
        pokemon = Pokemon("ENEMY", shiny=choice([True, False]),
                          level=Pokemon.pokemons[message.from_user.id].level + randint(-1, 1))
        bot.send_message(message.chat.id, "YOUR ENEMY IS...")
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())

        create_btns_for_moves(message)
    else:
        bot.reply_to(message, f"BATTLE has already been started!")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_pokemon = Pokemon.pokemons[message.from_user.id]

    if message.text in user_pokemon.moves_raw.keys():
        move = message.text
    else:
        move = None
    battle = Battle.battle
    if battle:
        enemy = Pokemon.pokemons["ENEMY"]
        use = user_pokemon.moves_raw[move].use()
        dealt_damage = int(use["damage"] * (1 - enemy.defense / 100))
        bot.reply_to(message, use["entry"])
        bot.send_message(message.chat.id, f"You have dealt {dealt_damage} damage")
        Pokemon.pokemons["ENEMY"].hp -= dealt_damage

        if Pokemon.pokemons["ENEMY"].hp < 0:
            Pokemon.pokemons["ENEMY"].hp = 0
        bot.send_message(message.chat.id, f"Enemy hp: {Pokemon.pokemons["ENEMY"].hp}")

        if Pokemon.pokemons["ENEMY"].hp <= 0:
            bot.send_message(message.chat.id, f"YOU WIN!")
            Battle.battle = False

            exp = Pokemon.pokemons["ENEMY"].level * 10 + randint(0, Pokemon.pokemons["ENEMY"].level * 10)
            old_level = user_pokemon.level
            bot.send_message(message.chat.id, f"You have earned {exp} exp!")

            Pokemon.pokemons[message.from_user.id].exp += exp
            Pokemon.pokemons[message.from_user.id].get_new_lvl()

            bot.send_message(message.chat.id, f"Your level has increased from {old_level}"
                                              f"to {Pokemon.pokemons[message.from_user.id].level}!")

            # exp and level
        else:
            enemy_move = choice(enemy.moves)
            bot.send_message(message.chat.id, f"Enemy's move: {enemy_move.name}")
            use = enemy_move.use()
            bot.send_message(message.chat.id, use["entry"])
            dealt_damage = int(use["damage"] * (1 - user_pokemon.defense / 100))
            Pokemon.pokemons[message.from_user.id].hp -= dealt_damage

            bot.send_message(message.chat.id, f"Enemy has dealt {dealt_damage} damage")

            if Pokemon.pokemons[message.from_user.id].hp < 0:
                Pokemon.pokemons[message.from_user.id].hp = 0
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
