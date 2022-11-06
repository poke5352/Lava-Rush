import random
import nextcord
import asyncio
import requests
import html

from nextcord import slash_command, SlashOption
from nextcord.ext.commands import Bot, Cog
from config import SLASH_GUILDS, EMBED_COLOR, FOOTER, START_TIME

import commands.game as game

# Join Button
class Join_Button(nextcord.ui.View):
    def __init__(self):
        super().__init__()
    
    @nextcord.ui.button(label="Join Game", style=nextcord.ButtonStyle.green)
    async def join(self, button, interaction):
        if game.games[interaction.guild.id].started == False:
            # Checks if player is already in game
            if interaction.user.id in game.games[interaction.guild.id].players:
                game.games[interaction.guild.id].players.remove(interaction.user.id)
                await interaction.response.send_message("You have left the game!", ephemeral=True)
            else:
                game.games[interaction.guild.id].players.append(interaction.user.id)
                await interaction.response.send_message("You have joined the game!", ephemeral=True)

            # Creates Embed
            embed = nextcord.Embed(
                    title = "Welcome to Lava Rise!",
                    description = "Waiting for players! Game Starts in " +  str(START_TIME) + " Seconds. Click button below to join the game:",
                    color = EMBED_COLOR
                )
            
            # Create Player List
            if len(game.games[interaction.guild.id].players) == 0:
                string = "```None```"
            else:
                string = "```\n"
                for player in game.games[interaction.guild.id].players:
                    string = string + interaction.guild.get_member(player).name + "\n"
                string = string + "```"

            embed.add_field(
                name = "Current Players:",
                value = string
            )

            embed.set_footer(text=FOOTER)
            view = Join_Button()
            await interaction.message.edit(embed=embed, view=view)


class Answer_Button(nextcord.ui.View):
    def __init__(self, question_id, answer, difficulty):
        super().__init__()
        self.id = question_id
        self.answer_choice = answer
        self.difficulty = difficulty

    @nextcord.ui.button(label="A", style=nextcord.ButtonStyle.blurple)
    async def answer_a(self, button, interaction):
        await self.answer(interaction, "A")
    
    @nextcord.ui.button(label="B", style=nextcord.ButtonStyle.blurple)
    async def answer_b(self, button, interaction):
        await self.answer(interaction, "B")

    @nextcord.ui.button(label="C", style=nextcord.ButtonStyle.blurple)
    async def answer_c(self, button, interaction):
        await self.answer(interaction, "C")

    @nextcord.ui.button(label="D", style=nextcord.ButtonStyle.blurple)
    async def answer_d(self, button, interaction):
        await self.answer(interaction, "D")
    
    async def answer(self, interaction, answer):
        await interaction.response.defer()
        if game.games[interaction.guild.id].started == True:
            if interaction.user.id in game.games[interaction.guild.id].eliminated:
                await interaction.response.send_message("You are already eliminated!", ephemeral=True)
            else:
                if self.id in game.games[interaction.guild.id].player_data[interaction.user.id]['questions_asked']:
                    game.games[interaction.guild.id].player_data[interaction.user.id]['questions_asked'].remove(self.id)
                    game.games[interaction.guild.id].player_data[interaction.user.id]['number_answered'] += 1
                    if answer == self.answer_choice:
                            
                        # Add Points
                        if self.difficulty == "easy":
                            game.games[interaction.guild.id].player_data[interaction.user.id]['score'] += 1
                            earned = "1"
                        elif self.difficulty == "medium":
                            game.games[interaction.guild.id].player_data[interaction.user.id]['score'] += 5
                            earned = "5"
                        elif self.difficulty == "hard":
                            game.games[interaction.guild.id].player_data[interaction.user.id]['score'] += 10
                            earned = "10"
            
                        await self.next_question(interaction, interaction.user.id, True, earned)
                    else:
                        await self.next_question(interaction, interaction.user.id, False, difficulty=self.difficulty, correct_answer=self.answer_choice)
                else:
                    await interaction.response.send_message("You have already answered!", ephemeral=True)
        else:
            await interaction.response.send_message("Game has not started!", ephemeral=True)

    async def next_question(self, interaction, player_id, correct, earned="0", difficulty=None, correct_answer=None):
        response = requests.get('https://opentdb.com/api.php?amount=1&category=17&type=multiple').json()
        question = response["results"][0]["question"]
        question = html.unescape(question)
        # Create Embed
        embed = nextcord.Embed(
            title = "Correct!" if correct else "Incorrect!",
            description = "You have advanced " + earned + " meters from lava!\n" + "Current Distance Away From Lava: " + str(round(game.games[interaction.guild.id].player_data[player_id]["score"]-game.games[interaction.guild.id].lava_level, 2)) + " meters\n Questions Answered: " + str(game.games[interaction.guild.id].player_data[player_id]["number_answered"]),
            color = EMBED_COLOR
        )
        if not correct:
            embed.set_thumbnail(url = "https://uxwing.com/wp-content/themes/uxwing/download/checkmark-cross/red-x-icon.png")
            
            if self.difficulty == "easy":
                penalty = 7*game.games[interaction.guild.id].penalty_modifier
            elif self.difficulty == "medium":
                penalty = 5*game.games[interaction.guild.id].penalty_modifier
            elif self.difficulty == "hard":
                penalty = 3*game.games[interaction.guild.id].penalty_modifier
            embed.add_field(
                name = "Correct Answer:",
                value = correct_answer,
                inline=False
            )
            embed.add_field(
                name = "Penalized!",
                value = "Since you got it wrong you have been frozen for **" + str(penalty) + " seconds**!",
                inline=False
            )
            embed.set_footer(text=FOOTER)
            await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio.sleep(penalty)
        
            embed = nextcord.Embed(
                title = "Next Question:",
                description = "You have advanced " + earned + " meters from lava!\n" + "Current Distance Away From Lava: " + str(round(game.games[interaction.guild.id].player_data[player_id]["score"]-game.games[interaction.guild.id].lava_level, 2)) + " meters\n Questions Answered: " + str(game.games[interaction.guild.id].player_data[player_id]["number_answered"]),
                color = EMBED_COLOR
            )


        
        if correct:
            embed.set_thumbnail(url = "https://uxwing.com/wp-content/themes/uxwing/download/checkmark-cross/small-check-mark-icon.png")
        
        embed.add_field(
            name = "Question:",
            value = question,
            inline=False
        )
        embed.add_field(
            name = "Category:",
            value = response["results"][0]["category"]
        )
        embed.add_field(
            name = "Difficulty:",
            value = response["results"][0]["difficulty"]
        )

        
        # Remove HTML Character Codes
        response["results"][0]["correct_answer"] = html.unescape(response["results"][0]["correct_answer"])
        for i in range(3):
            response["results"][0]["incorrect_answers"][i] = html.unescape(response["results"][0]["incorrect_answers"][i])

        # Shuffle Choices
        choices = [response["results"][0]["correct_answer"], response["results"][0]["incorrect_answers"][0], response["results"][0]["incorrect_answers"][1], response["results"][0]["incorrect_answers"][2]]
        
        random.shuffle(choices)
        answer_choices = ["A", "B", "C", "D"]
        answer = answer_choices[choices.index(response["results"][0]["correct_answer"])]

        embed.add_field(
            name = "Choices:",
            value = "```A: " + choices[0] + "\nB: " + choices[1] + "\nC: " + choices[2] + "\nD: " + choices[3] + "```",
            inline= False
        )

        embed.set_footer(text=FOOTER)
        question_id = random.randint(0,100000000000)
        # Add question id to players
        game.games[interaction.guild.id].player_data[player_id]['questions_asked'].append(question_id)

        view = Answer_Button(question_id, answer, response["results"][0]["difficulty"])

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        
class Start(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="start",
        description="Start Game",
        guild_ids=SLASH_GUILDS
    )
    async def start(self, ctx, penalty_modifier=SlashOption(description="Multiplier for the penalty for getting a question wrong", required=False, default=1), lava_speed=SlashOption(description="Speed of the lava", required=False, default=0.1)):
        # Checks if game exists in guild
        if ctx.guild.id in game.games:
            await ctx.send("Game already in progress")
        else:
            game.games[ctx.guild.id] = game.Game()
            game.games[ctx.guild.id].penalty_modifier = float(penalty_modifier)

            # Creates Embed
            embed = nextcord.Embed(
                title = "Welcome to Lava Rise!",
                description = "Waiting for players! Game Starts in " +  str(START_TIME) + " Seconds. Click button below to join the game:",
                color = EMBED_COLOR

            )
            embed.add_field(
                name = "Current Players:",
                value = "```None```"
            )

            embed.set_footer(text=FOOTER)
            view = Join_Button()
            await ctx.response.send_message(embed=embed, view=view)

            await asyncio.sleep(START_TIME)
            await self.start_game(ctx, lava_speed)
    
    # Start Sequence
    async def start_game(self, ctx, lava_speed):
        game.games[ctx.guild.id].started = True

        # Mention all players
        string = ""
        for player in game.games[ctx.guild.id].players:
            string = string + ctx.guild.get_member(player).mention + ", "
        
        # Remove last comma
        string = string[:-2]

        await ctx.send("Game has started! Players: " + string)

        # Create Player Data
        for player in game.games[ctx.guild.id].players:
            game.games[ctx.guild.id].player_data[player] = {
                "number_answered": 0,
                "score": 1,
                "questions_asked": []
            }
        #await self.statistics(ctx)
        await self.game_loop(ctx, float(lava_speed))
    
    # Game Loop
    async def game_loop(self, ctx, lava_speed):
        await self.first_question(ctx)
        speed = 0.1
        while True:
            for player in game.games[ctx.guild.id].players:
                if not (player in game.games[ctx.guild.id].eliminated):
                    if(game.games[ctx.guild.id].player_data[player]['score'] < game.games[ctx.guild.id].lava_level):
                        await ctx.send(ctx.guild.get_member(player).mention + " has been eliminated!")
                        game.games[ctx.guild.id].eliminated.append(player)

            await asyncio.sleep(5)
            speed += lava_speed
            game.games[ctx.guild.id].lava_level += speed
            await ctx.guild.me.edit(nick="Lava Bot - " + str(round(game.games[ctx.guild.id].lava_level, 2)) + " meters")
            if(len(game.games[ctx.guild.id].eliminated) == len(game.games[ctx.guild.id].players)):
                await self.end_game(ctx)
                break


    # Show Game Statistics
    async def statistics(self, ctx):
        embed = nextcord.Embed(
            title = "Game Over",
            description = "Leaderboard:",
            color = EMBED_COLOR
        )
        game.games[ctx.guild.id].eliminated.reverse()
        for player in game.games[ctx.guild.id].eliminated:
            embed.add_field(
                name = ctx.guild.get_member(player).display_name + ":",
                value = "Total Distance Travelled: " + str(game.games[ctx.guild.id].player_data[player]["score"]) + " meters\n Questions Answered: " + str(game.games[ctx.guild.id].player_data[player]["number_answered"]),
                inline= False
            )
        embed.set_footer(text=FOOTER)
        await ctx.channel.send(embed=embed)

    # Question shown to everyone in beginning
    async def first_question(self, ctx):
        response = requests.get('https://opentdb.com/api.php?amount=1&category=17&type=multiple').json()
        question = response["results"][0]["question"]
        question = html.unescape(question)

        # Create Embed
        embed = nextcord.Embed(
            title = "Question: ",
            description = question,
            color = EMBED_COLOR
        )
        embed.add_field(
            name = "Category:",
            value = response["results"][0]["category"]
        )
        embed.add_field(
            name = "Difficulty:",
            value = response["results"][0]["difficulty"]
        )
        
        # Remove HTML Character Codes
        response["results"][0]["correct_answer"] = html.unescape(response["results"][0]["correct_answer"])
        for i in range(3):
            response["results"][0]["incorrect_answers"][i] = html.unescape(response["results"][0]["incorrect_answers"][i])

        # Shuffle Choices
        choices = [response["results"][0]["correct_answer"], response["results"][0]["incorrect_answers"][0], response["results"][0]["incorrect_answers"][1], response["results"][0]["incorrect_answers"][2]]
        
       

        choices2 = []
        for choice in choices:
            choices2.append(html.unescape(choice))
        choices = choices2

        random.shuffle(choices)
        answer_choices = ["A", "B", "C", "D"]
        answer = answer_choices[choices.index(response["results"][0]["correct_answer"])]

        embed.add_field(
            name = "Choices:",
            value = "```A: " + choices[0] + "\nB: " + choices[1] + "\nC: " + choices[2] + "\nD: " + choices[3] + "```",
            inline= False
        )

        embed.set_footer(text=FOOTER)
        question_id = random.randint(0,100000000000)
        # Add question id to players
        for player in game.games[ctx.guild.id].players:
            game.games[ctx.guild.id].player_data[player]["questions_asked"].append(question_id)

        view = Answer_Button(question_id, answer, response["results"][0]["difficulty"])

        await ctx.channel.send(embed=embed, view=view)


    # End Game
    async def end_game(self, ctx):
        await ctx.guild.me.edit(nick="Lava Rush")
        await self.statistics(ctx)
        del game.games[ctx.guild.id]

    # Force End Game
    @slash_command(
        name="endgame",
        description="Force End Game",
        guild_ids=SLASH_GUILDS
    )
    
    async def force_end_game(self, ctx):
        if ctx.guild.id in game.games:
            await ctx.send("Game has been forcefully ended.")
            for player in game.games[ctx.guild.id].players:
                if not (player in game.games[ctx.guild.id].eliminated):
                    await ctx.send(ctx.guild.get_member(player).mention + " has been eliminated!")
                    game.games[ctx.guild.id].eliminated.append(player)
            await self.end_game(ctx)
        else:
            await ctx.send("Game is not running.")

        

        


def setup(bot: Bot) -> None:
    bot.add_cog(Start(bot))
