from typing import List, Any, Coroutine

import discord
import random
import os
from dotenv import load_dotenv


load_dotenv()
client = discord.Client()


HangLives = 3


@client.event
async def on_ready():
    print(f'{client.user} has connected')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send('Hello')
    if message.content.endswith('?'):
        n = random.randint(1, 1000)
        if n % 2:
            await message.channel.send('Yes')
        else:
            await message.channel.send('No')
    if message.content.startswith("$game"):
        await message.channel.send("Select which game you'd like to play\n"
                                   "-hangman\n"
                                   "-number (under construction)")
        response = await client.wait_for('message', check=lambda m: m.author == message.author)
        ans = response.content
        if ans == "hangman":
            await hangman(message)
        elif ans == "number":
            # await numbers(message)
            await message.channel.send("I SAID UNDER CONSTRUCTION")
        else:
            await message.channel.send("invalid response you idiot")


async def numbers(message):
    start = 0
    finish = 100
    answer = random.randint(start, finish)
    await message.channel.send(f"I have thought of a random number between {start} and {finish}")
    guess = await (getNumGuess(message, start, finish))
    while guess != answer:
        if answer < guess < finish:
            finish = guess
        elif start < guess < answer:
            start = guess
        await message.channel.send(f"The number is between {start} and {finish}, keep guessing!")
        guess = await getNumGuess(message, start, finish)
    await message.channel.send(f"Correct! The number is {answer}")


async def getNumGuess(message, start, finish):
    response = await client.wait_for('message', check=lambda m: m.author == message.author)
    num = int(response.content)

    return 0


async def hangman(message):
    with open("words_alpha.txt") as f:
        lines = f.readlines()
        key = random.choice(lines)
    key = key[:-1]
    display: list[str] = [" -- " for i in range(len(key))]
    print(key)
    guessed = []
    lives = HangLives
    curr = "".join(display)
    await message.channel.send(
        "Let's play hangman! Type quit to leave.\n"
        f"Enter a guess to start! You have {str(lives)} lives.\n"
        f"{curr}")
    guess = await getGuess(message, guessed)
    display = updateDisplay(display, guess, key)
    guessed.append(guess.upper())
    while "".join(display) != key:
        curr = "".join(display)
        done = "".join(guessed)
        if guess == "quit":
            break
        if guess in list(key):
            await message.channel.send(
                "Correct! Enter a guess!\n"
                f"You currently have {curr}\n"
                f"You have guessed {done}\n"
                f"You have {str(lives)} lives left.")
        else:
            lives = lives - 1
            if lives == 0:
                break
            await message.channel.send(
                "Incorrect! Enter a guess!\n"
                f"You currently have {curr}\n"
                f"You have guessed {done}\n"
                f"You have {str(lives)} lives left.")
        guess = await getGuess(message, guessed)
        display = updateDisplay(display, guess, key)
        guessed.append(guess.upper())
    if lives == 0 or guess == "quit":
        await message.channel.send("Congrats, you are trash. The correct word is " + key)
    else:
        await message.channel.send("Congrats! The correct word is " + key)


def updateDisplay(display, guess, key):
    for i in range(len(key)):
        if guess == key[i]:
            display[i] = guess
    return display


async def getGuess(message, guessed):
    response = await client.wait_for('message', check=lambda m: m.author == message.author)
    guess = response.content
    while (len(guess) != 1 or guess.upper() in guessed) and guess.lower() != "quit":
        done = "".join(guessed)
        await message.channel.send("Invalid guess you idiot! You have guessed " + done + " so far")
        response = await client.wait_for('message', check=lambda m: m.author == message.author)
        guess = response.content
    return guess.lower()


client.run(os.getenv("TOKEN"))
