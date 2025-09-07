import telebot 
from config import token

from logic import Pokemon

bot = telebot.TeleBot(token) 



@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.id not in Pokemon.pokemons.keys():
        pokemon = Pokemon(message.from_user.id)
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "Ты уже создал себе покемона")


@bot.message_handler(commands=['turn'])
def show(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        Pokemon.pokemons[message.from_user.id].turn()
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.reply_to(message, f"Your pokemon orientation has been changed to {pokemon.possible_orientations[pokemon.front]}")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "You do not have any pokemon. Use '/go' to create one!")


@bot.message_handler(commands=['shine'])
def show(message):
    if message.from_user.id in Pokemon.pokemons.keys():
        Pokemon.pokemons[message.from_user.id].shine()
        pokemon = Pokemon.pokemons[message.from_user.id]
        bot.reply_to(message, f"Your pokemon is {pokemon.possible_shiny[pokemon.shiny]} now!")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "You do not have any pokemon. Use '/go' to create one!")

bot.infinity_polling(none_stop=True)

