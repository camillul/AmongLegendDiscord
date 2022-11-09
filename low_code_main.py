from ipaddress import v4_int_to_packed
from mimetypes import init
from multiprocessing.sharedctypes import Value
import numbers
from turtle import right
import discord
from discord.ext.commands import Bot
from discord import Member, User
from discord.ext import commands, tasks
from discord import Guild, TextChannel, Role
from discord.utils import get

import schedule
import random
import sys
from typing import Union
from constants import *
import time

from constants import *


#TODO:Each role should be a class or a data structure.

#____________________________________________________AMONG LEGEND CLASS__________________________________________

class AmongLegend():
    def __init__(self, bot):
        self.init = False
        self.start = False
        self.finish = False
        self.vote = False
        self.vote_dict = {}
        self.time_start = 0
        self.bot = bot
        self.nb_joueur = 0
        self.emoji_role_dict = {'😈': "Imposteur" , '💏': "Romeo", '🐍': "Serpentin", '🤖':"Droide", '🕵️': "Escroc", '🎭': "Double-face", '🦸‍♀️': "Super-héro"}
        self.emoji_role = [ '😈' , '💏', '🐍', '🤖', '🕵️', '🎭', '🦸‍♀️']
        self.emoji_role_str = ["Imposteur", "Romeo", "Serpentin", "Droide","Escroc", "Double-face","Super-héro"]
        self.vote_role_messages = []
        self.player_role_messages = {}
        self.role_messages_player = {} #reserve of player_role_message : give message concern from player
        self.discord_member_player = []
        self.discord_name_player = []
        self.players_role = {}
        self.player_victory = {}
        self.player_score_dict = {}
        self.romeo_dict = {}
        self.player_double_face_dict = {}
        self.role_list = []
        self.droide_quest_copy = DROIDE_QUEST
        self.droide_ultime_quest_copy = LONG_TERM_DROIDE_QUEST
        self.double_face_face = DOUBLE_FACE_FACE
        self.player_quest_dict = {}
        self.droide_quest_frequency = 5 * 60 # secondes
        self.double_face_frequency = 2 * 60 # secondes
        self.all_role = ["Droide", "Serpentin", "Droide", "Double-face", "Romeo","Imposteur", "Super-hero", "Escroc", "Romeo", "Double-face" ]


    def charge_guild(self):
        self.serveurGMP = self.bot.get_guild(SERVEUR_ID)
        self.channel_game_start = self.bot.get_channel(GAME_START_ID)
        self.channel_general = self.bot.get_channel(GENERAL_ID)
        self.salon_faille = self.bot.get_channel(FAILLE_ID)
        self.channel_score = self.bot.get_channel(FAILLE_ID)

    def AmongLegendInit(self):
        self.emoji_dict = {}
        for n in range(len(self.emoji_role)-1):
            self.emoji_dict[self.emoji_role[n]] = self.emoji_role_str[n]

    def get_game_time(self):
        if (self.time_start != 0):
            return time.time() - self.time_start

    def get_players(self):
        self.nb_joueur = len(self.salon_faille.members)
        self.discord_member_player = []
        self.discord_name_player = []
        for j in self.salon_faille.members:
            self.discord_member_player.append(j)
            self.discord_name_player.append(j.name)
            self.player_score_dict[j] = 0
            self.player_victory[j] = False
        
    def get_role_list(self):
        self.role_list = []
        role_remaining = self.all_role.copy()
        for i in range(self.nb_joueur) :
            self.role_list.append(role_remaining.pop(random.randint(0,len(role_remaining)-1)))
        print(self.role_list)

    def role_distribution(self):
        self.get_role_list()
        random.shuffle(self.role_list)
        new_role_list = self.role_list.copy()
        i = 0
        for a in self.salon_faille.members:
            self.players_role[a] = new_role_list[i]
            i += 1

    def droide_quest(self, player):
 
        if self.players_role[player] == "Droide" :
            if (len(self.player_quest_dict[player]) == 0):
                quest_ultime = self.droide_ultime_quest_copy[random.randint(0,len(self.droide_ultime_quest_copy)-1)]
                quest_ultime = self.droide_ultime_quest_copy[random.randint(0,len(self.droide_ultime_quest_copy)-1)]
                self.player_quest_dict[player].append(quest_ultime)
                return quest_ultime
            else : 
                quest = self.droide_quest_copy[random.randint(0,len(self.droide_quest_copy)-1)]
                self.player_quest_dict[player].append(quest)
                return quest 
        else:
            return ""

    def double_face_quest(self, player ):
        if self.players_role[player] == "Double-face" :
            if ( self.get_game_time() - len(self.player_double_face_dict[player]) * self.double_face_frequency >= 0):
                if self.player_double_face_dict[player][-1] == self.double_face_face[0]:
                    self.player_double_face_dict[player].append(self.double_face_face[1])
                else :
                    self.player_double_face_dict[player].append(self.double_face_face[0])

                return self.player_double_face_dict[player][-1]
            else:
                return ""
        else:
            return ""

    def score_result(self):
        for p in self.discord_member_player:

            for voted_p in self.discord_member_player:
                if p != voted_p:
                    if self.vote_dict[p].is_player_vote_right(voted_p):
                        self.player_score_dict[p] += 1

            if self.vote_dict[p].is_role_discovered():
                    self.player_score_dict[p] -= 2

            if self.player_victory[p]:
                if (self.players_role == "Escroc" or self.players_role == "Super_hero") :
                    self.player_score_dict[p] += int(self.nb_joueur/2) + 3
                else:
                    self.player_score_dict[p] += int(self.nb_joueur/2)

        str_score = ""
        for p in self.discord_member_player:
            str_score += f"{p.name} a obtenu : {self.player_score_dict[p]} point(s)\n !"
        return str_score
    
    def has_everyone_voted(self):
        missing_vote = []
        for p in self.discord_member_player:
            if not self.vote_dict[p].has_finished_vote():
                missing_vote.append(str(p.name))
        if len(missing_vote) == 0:
            return ""
        else: 
            return "Le(s) joueurs suivant(s) n'ont pas encore voté {m}! ".format(m = missing_vote)
                

#_____________________________________________________VOTE CLASS _________________________________________________________

class Vote():
    def __init__(self, game, my_role) -> None:
        self.game = game
        self.my_role = my_role
        self.my_vote_dict = {}
        self.nb_vote = 0 
        self.right_vote = 0

    def is_player_vote_right(self,voted_player):
        if self.game.players_role[voted_player] == self.my_vote_dict[voted_player]:
            return True
        else:
            return False

    def add_vote_to_player(self,member,reaction):
        self.my_vote_dict[member] = self.game.emoji_role_dict[reaction.emoji]
        self.nb_vote += 1
        if self.game.emoji_role_dict[reaction.emoji] == self.game.players_role[member]:
            self.game.vote_dict[member].right_vote += 1

    def remove_vote_to_player(self,member,reaction):
        self.my_vote_dict[member] = None
        self.nb_vote -= 1
        if self.game.emoji_role_dict[reaction.emoji] == self.game.players_role[member]:
            self.game.vote_dict[member].right_vote -= 1

    def count_vote_number(self):
        return self.nb_vote

    def has_finished_vote(self):
        if self.nb_vote == self.game.nb_joueur - 1:
            return True
        else:
            return False

    def is_role_discovered(self):
        if (self.right_vote >= self.nb_vote/2):
            return True
        else:
            return False
        
        
# _________________________________________________DISCORD COMMAND___________________________________________________________________
command_prefix='//'
intents = None   
bot = commands.Bot(command_prefix=command_prefix, intents = None)
Game = AmongLegend(bot)

@commands.command(name = "reset")
async def reset(ctx, *args):
    del Game
    Game = AmongLegend(bot)
    await Game.channel_game_start.send("Game reset !\n")

@commands.command(name = "call")
async def call(ctx, *args):
    Game.init = True
    await Game.channel_game_start.send(f"{AMONGLEGEND_TITLE}\nUne game de Among Legend va commencer ! Préparez-vous invocateurs ! Venez dans le salon {Game.salon_faille.name} \n\tConfirmer le nombre de joueur et commencer la distribution des rôle avec {command_prefix}start \n\tAnnoncer au bot le début de la game par la commande {command_prefix}clock_in et n'oubliez pas d'annoncer la fin par un {command_prefix}clock_out\n\n")

@commands.command(name = "start_aram")
async def start_aram(ctx, *args):
    #TODO: make a different initialization in aram
    pass

@commands.command(name = "start_faille")
async def start_faille(ctx, *args):
    if (Game.init):
        Game.start = True
        Game.get_players()
        Game.role_distribution()
        for p in Game.discord_member_player:
            if Game.players_role[p] == "Romeo":
                await p.send(f"Ton rôle attribué est le {Game.players_role[p]}, je te laisse verifier ta mission principale sur le salon 'rôles' ! \n\tIl Ta Juliette sera choisi aléatoirement ! Pour cela utilise la commande suivante : \n{command_prefix}juliette \n ")
            elif Game.players_role[p] == "Double-face" :
                Game.player_double_face_dict[p] = [Game.double_face_face[random.randint(0, 1)],]
                await p.send(f"Ton rôle attribué est le {Game.players_role[p]}, je te laisse verifier ta mission principale sur le salon 'rôles' ! \n\t Tu vas commencer en tant que Double-face : {Game.player_double_face_dict[p][-1]}")
            elif Game.players_role[p] == "Droide" : 
                Game.player_quest_dict[p] = []
                await p.send(f"Ton rôle attribué est le {Game.players_role[p]}, je te laisse verifier ta mission principale sur le salon 'rôles' ! \n\tTu vas recevoir des missions et devoir les remplir tout en gagnant ta partie. Une mission 'ultime' qui sera une mission qui peut être rempli à n'importe quel moment mais devra être completé à la fin de la partie. D'autres missions secondaires apparaîtront et devront être exécuté immédiatement !")
                
            else:
                await p.send(f"Ton rôle attribué est le {Game.players_role[p]}, je te laisse verifier ta mission principale sur le salon 'rôles' ! \n")

        await Game.channel_game_start.send(f"Une game de {Game.nb_joueur} joueurs/joueuses : {Game.discord_name_player} va débuter ! les rôles ont été données en message privé aux participant\n")


@tasks.loop(seconds= Game.droide_quest_frequency)
async def task_quest_droide():
    for player in Game.discord_member_player :
        str_to_send = Game.droide_quest(player)
        if str_to_send != "":
            await player.send(str_to_send)

@tasks.loop(seconds= Game.double_face_frequency)
async def task_quest_double_face():
    for player in Game.discord_member_player :
        str_to_send = Game.double_face_quest(player)
        if str_to_send != "":
            await player.send(str_to_send)

@commands.command(name = "clock_in")
async def clock_in(ctx, *args):
    if (Game.start):
        Game.time_start = time.time()
        task_quest_double_face.start()
        task_quest_droide.start()

@commands.command(name = "clock_out")
async def clock_out(ctx, *args):
    task_quest_double_face.stop()
    task_quest_droide.stop()
    await  Game.channel_game_start.send(f"\nCette game est terminée ! Commencer le débat pour démasquer les rôles. \n\tTaper {command_prefix}end quand vous avez fini le débat afin de révélez les rôle de tout le monde et comptabiliser les points\n\n ")
    for p in Game.discord_member_player:
        Game.vote_dict[p] = Vote(Game, Game.players_role[p])
        await Game.channel_game_start.send(f"Quel est le rôle de {p} ?")
        last_message = Game.channel_game_start.last_message
        for e in Game.emoji_role:
            await last_message.add_reaction(e)
        Game.vote_role_messages.append(last_message)
        Game.player_role_messages[p] = last_message
        Game.role_messages_player[last_message] = p
    for m in Game.vote_role_messages:
        print(m.content)

@commands.command(name = "vote")
async def vote(ctx, *args):
    msg = Game.has_everyone_voted()
    if  msg == "":
        Game.vote = True
        await Game.channel_game_start.send(f"Le compte est bon ! Pour afficher les resultats, utiliser la commande {command_prefix}end !")
    else:

        await Game.channel_game_start.send("Le compte des votes n'est pas bon ! Veuillez voter pour chaque personne 1 seule fois et ne pas vous voter vous-même merci. "+msg+"  !\nCordialement,\nle bureau des votes")

@commands.command(name = "win_quest")
async def win(ctx, *args):
    Game.player_victory[Game.salon_faille.guild.get_member(ctx.message.author.id)] = True
    await Game.salon_faille.guild.get_member(ctx.message.author.id).send("La victoire de ton rôle à bien été pris en compte dans le score !")

@commands.command(name = "loose_quest")
async def loose(ctx, *args):
    Game.player_victory[Game.salon_faille.guild.get_member(ctx.message.author.id)] = False
    await Game.salon_faille.guild.get_member(ctx.message.author.id).send("La non-victoire de ton rôle à bien été pris en compte dans le score !")

@commands.command(name = "end")
async def end(ctx, *args):
    if Game.vote:
        str_revelation = ""
        for p in Game.discord_member_player:
            if Game.players_role[p] == "Romeo":
                try:
                    str_revelation += f'{p} était {Game.players_role[p]} ! et {Game.romeo_dict[p]} était sa Juliette, trop mignon <3 !\n'
                except:
                    str_revelation += f'{p} était {Game.players_role[p]} !\n '
            elif Game.players_role[p] == "Droide" :
                str_quest = ""
                for q in Game.player_quest_dict[p]:
                    str_quest += f"\n{q}" 
                str_revelation += f'{p} était {Game.players_role[p]} ! et voici le récapitulatif de toute ses quêtes : {str_quest}\n'
            else:
                str_revelation += f'{p} était {Game.players_role[p]} !'
            await Game.channel_game_start.send(str_revelation)
            str_revelation = ""

        score = Game.score_result()
        await Game.channel_game_start.send("---------------------SCORE---------------------")            
        await Game.channel_game_start.send(score)
        await Game.channel_game_start.send("--------------------SCORE---------------------")    
        await Game.channel_game_start.send(f"Merci d'avoir joué à Among Legend et à une prochaine ! <3\n\n {SEPARATOR}\n\nCrédits : Copyright from Solary\n\tBot developpeurs : RickyBeater, YouStones \n\tContributeur(se)s) : Swan, Shaiht, Lorenzo-P, Nysciciel, Joris, Atmix \n\n{SEPARATOR} \n\n")
    else:
        await Game.salon_faille.guild.get_member(ctx.message.author.id).send(f"Le vote n'as pas encore été fait ! ")

@commands.command(name = "clear_game_channel")
async def clear_game_channel(ctx, amount = 100):
    await Game.channel_game_start.purge(limit=amount)

    
@commands.command(name = "juliette")
async def juliette(ctx, *args):
    if Game.players_role[Game.salon_faille.guild.get_member(ctx.message.author.id)] == "Romeo" :
        selected_juliette = Game.discord_member_player[random.randint(0, len(Game.discord_member_player)-1)]
        while(selected_juliette == Game.salon_faille.guild.get_member(ctx.message.author.id)):
            selected_juliette = Game.discord_member_player[random.randint(0, len(Game.discord_member_player)-1)]
        await Game.salon_faille.guild.get_member(ctx.message.author.id).send(f"Votre  Juliette est {selected_juliette} <3 trop mignon ! Si c'est un allié vous avez 30s pour mourir avec Juliette et si c'est un ennemie vous n'avez pas le droit de participer à son elimination\n ")
        Game.romeo_dict[Game.salon_faille.guild.get_member(ctx.message.author.id)] = args[0]
    else :
        await Game.salon_faille.guild.get_member(ctx.message.author.id).send(f"ERROR 404, tu n'es pas Romeo ... N'essaye plus jamais de m'arnaquer !")

@bot.event
async def on_ready():
    Game.charge_guild()
    Game.AmongLegendInit()
    print("AmongLegendBot ready !")

@bot.event
async def on_reaction_add(reaction, user):
    voting_player = Game.salon_faille.guild.get_member(user.id)
    player_target = Game.role_messages_player[reaction.message]
    print(voting_player)
    print(player_target)
    if user.name != "AmongLegend" and voting_player != player_target:
        Game.vote_dict[voting_player].add_vote_to_player(player_target, reaction)
@bot.event
async def on_reaction_remove(reaction, user):
    voting_player = Game.salon_faille.guild.get_member(user.id)
    player_target = Game.role_messages_player[reaction.message]
    print(voting_player)
    print(player_target)
    if user.name != "AmongLegend" and voting_player != player_target :
        Game.vote_dict[voting_player].remove_vote_to_player(player_target, reaction)


bot.add_command(reset)
bot.add_command(call)
bot.add_command(start_faille)
bot.add_command(start_aram)
bot.add_command(clock_in)
bot.add_command(clock_out)
bot.add_command(juliette)
bot.add_command(win)
bot.add_command(loose)
bot.add_command(vote)
bot.add_command(end)
bot.add_command(clear_game_channel)

bot.run(TOKEN)  