# -*- coding: utf-8  -*-

import asyncio
import requests
import json

import discord
from requests.auth import HTTPBasicAuth


class Shobot(discord.Client):
    token = "MzkxNjU3NzkwNTI5MzM5Mzky.Ds4d0A.0TLZHalY_NLbv4eK0aAfottaYjw"  # Mettez dans cette variable le token du bot
    trust = ["Shobu13#3927",
             "Utilisateur 2"]  # Mettez dans cette variable les utilisateurs pouvant utiliser les commandes restreintes
    trust_roles = ["Admin", "Modo"]
    ranks = False

    bot_name = 'Saucisse'

    ver = "1.5.0"
    lang = "fr"

    blacklist = []

    async def check_blacklist(self):
        global blacklist
        await self.wait_until_ready()
        while not self.is_closed:
            response = requests.get("http://127.0.0.1:8000/bot/word_blacklist/").json()
            blacklist = response.get('words')
            assert isinstance(blacklist, str)
            blacklist = blacklist.replace(" ", "")
            blacklist = blacklist.split(";")
            await asyncio.sleep(60)

    async def on_ready(self):
        print(self.bot_name + " " + self.ver + " " + self.lang)
        server = self.get_first_server()
        assert isinstance(server, discord.server.Server)
        self.loop.create_task(self.check_blacklist(), )

    @asyncio.coroutine
    def on_message(self, message):
        print(blacklist)
        rep = text = msg = message.content
        rep2 = text2 = msg2 = rep.split()
        user = str(message.author)
        user_bot_self = str(self.user)
        user_bot = user_bot_self.split("#")[0]
        role_trusted = False
        pm = message.server is None
        if not pm:
            server_msg = str(message.channel.server)
            chan_msg = str(message.channel.name)
            for role_name in self.trust_roles:
                if ":" in role_name and role_name.split(":")[0] == server_msg:
                    rank_role = discord.utils.get(message.server.roles,
                                                  name=":".join(role_name.split(":")[1:]))
                else:
                    rank_role = discord.utils.get(message.server.roles, name=role_name)
                if isinstance(rank_role, discord.role.Role) and rank_role.id in [r.id for r in
                                                                                 message.author.roles]:
                    role_trusted = True
        else:
            server_msg = user
            chan_msg = user
        trusted = user in self.trust or role_trusted
        try:
            command = rep2[0].lower()
            params = rep2[0:]
        except IndexError:
            command = ""
            params = ""

        print(user + " (" + server_msg + ") [" + chan_msg + "] : " + rep)

        if self.ranks and not pm and user != user_bot_self:
            open("msgs_user_" + server_msg + ".txt", "a").close()
            msgs = open("msgs_user_" + server_msg + ".txt", "r")
            msgs_r = msgs.read()
            if user not in msgs_r or user != user_bot_self:
                with open("msgs_user_" + server_msg + ".txt", "a") as msgs_w:
                    msgs_w.write(user + ":0\n")
                msgs.close()
                msgs = open("msgs_user_" + server_msg + ".txt", "r")
                msgs_r = msgs.read()
            msgs_user = msgs_r.split(user + ":")[1]
            msgs.close()
            user_msgs_n = int(msgs_user.split("\n")[0])
            user_msgs_n += 1
            msgs_r = msgs_r.replace(user + ":" + str(user_msgs_n - 1),
                                    user + ":" + str(user_msgs_n))
            with open("msgs_user_" + server_msg + ".txt", "w") as msgs:
                msgs.write(msgs_r)

        # Début des commandes
        if command == "!commandtest":  # Copiez ce code pour créer une commande
            yield from self.send_message(message.channel, "Texte à envoyer.")

        if command == "!ban" and trusted and not pm:  # Cette commande n'est pas utilisable en MP
            if "<@" in params[1] and ">" in params[
                1]:  # La variable params[1] est le premier paramètre entré par l'utilisateur. Si le premier paramètre est une mention
                id_user = message.server.get_member(params[1].replace("<@", "").replace(">",
                                                                                        ""))  # l'ID de l'utilisateur de la mention est récupéré
            else:  # sinon
                id_user = message.server.get_member_named(
                    params[1])  # le pseudo entré en premier paramètre est recherché
            try:
                yield from self.ban(id_user, int(params[
                                                     2]))  # bannissement de l'utilisateur avec l'ID de l'utilisateur avec le nombre de messages à effacer
            except IndexError:  # si le 2ème paramètre n'est pas mis (erreur)
                yield from self.ban(id_user,
                                    0)  # bannissement de l'utilisateur avec l'ID de l'utilisateur sans le nombre de messages à effacer

        if command == "!bing":  # Cette commande sert à rechercher sur Bing
            yield from self.send_message(message.channel,
                                         "https://www.bing.com/search?q=" + "+".join(
                                             params[
                                             1:]))  # "+".join(params[1:]) sert à séparer les paramètres de la commande par des + pour que l'URL de recherche soit accessible, par exemple, en tapant !bing test 2, le bot renverra https://www.bing.com/search?q=test+2

        if command == "!create_channel" and trusted and not pm:  # Cette commande sert à créer un channel sur le serveur, " ".join(params[1:]) est le nom du channel et " ".join() sert à mettre les mots de params[1:] qui est une partie de la liste params qui contient tous les mots du message (à part la commande qui est params[0]).
            yield from self.create_channel(message.server, " ".join(params[1:]))

        if command == "!create_channel_voice" and trusted and not pm:  # Cette commande sert à créer un channel vocal, voir la commande précédente.
            yield from self.create_channel(message.server, " ".join(params[1:]),
                                           type=discord.ChannelType.voice)

        if command == "!delete" and trusted and not pm:  # Cette commande sert à supprimer un message avec un ID.
            message_del = self.get_message(message.channel, params[1])
            yield from self.delete_message(message_del)

        if command == "!google":  # Voir la commande !bing
            yield from self.send_message(message.channel,
                                         "https://www.google.com/#q=" + "+".join(params[1:]))

        if command == "!invite":  # Cette commande sert à générer une invitation pour le serveur. Voir la commande !ban
            try:
                invite = yield from self.create_invite(message.channel, max_age=params[1])
            except IndexError:
                invite = yield from self.create_invite(message.channel)
            yield from self.send_message(message.channel,
                                         invite.url)  # Renvoie le lien de l'url de l'invitation

        if command == "!kick" and trusted and not pm:  # Voir la commande !ban
            if "<@" in params[1] and ">" in params[1]:
                id_user = message.server.get_member(params[1].replace("<@", "").replace(">", ""))
            else:
                id_user = message.server.get_member_named(params[1])
            yield from self.kick(id_user)

        if command == "!nick" and trusted and not pm:  # Ici, on a une commande qui change le nom du bot
            yield from self.change_nickname(self.user, " ".join(params[1:]))

        if (
                command == "!prune_members" or command == "!purge_members") and trusted and not pm:  # Cette commande sert à purger les membres inactifs.
            try:
                yield from self.prune_members(message.server, days=int(params[1]))
            except IndexError:  # params[1] est le nombre de jours depuis la dernière connexion des membres, si le paramètre n'est pas mis, le bot purgera les membres qui ne sont pas connectés depuis 30 jours
                yield from self.prune_members(message.server, days=30)

        if (
                command == "!purge" or command == "!clear") and trusted and not pm:  # Cette commande sert à effacer les messages, en tapant !purge 10, le bot supprimera les 10 derniers messages.
            yield from self.purge_from(message.channel, limit=int(params[
                                                                      1]))  # Cette ligne sert à supprimer les messages avec params[1] qui est le premier paramètre (le nombre de messages), il y a int(params[1]) car le paramètre doit être converti en un nombre.

        if (
                command == "!quit" or command == "!exit") and trusted:  # Cette commande sert à fermer le bot
            yield from self.close()

        if (
                command == "!rename_channel" or command == "!nick_channel") and trusted and not pm:  # Ici, il y a une commande qui renomme le channel où le message est envoyé
            yield from self.edit_channel(message.channel, name=" ".join(params[1:]))

        if command == "!role_user_add" and trusted and not pm:  # Cette commande sert à ajouter un rôle à un utilisateur
            if "<@" in params[1] and ">" in params[1]:
                member = message.server.get_member(params[1].replace("<@", "").replace(">", ""))
            else:
                member = message.server.get_member_named(params[1])
            role = discord.utils.get(message.server.roles, name=" ".join(params[
                                                                         2:]))  # cette ligne sert à récupérer le rôle de l'utilisateur à ajouter, " ".join(params[2:]) est le nom du rôle
            yield from self.add_roles(member,
                                      role)  # cette ligne sert à appliquer l'ajout du rôle à l'utilisateur et member est l'identifiant de l'utilisateur et role est l'identifiant du rôle

        if command == "!role_user_remove" and trusted and not pm:  # Cette commande sert à retirer un rôle à un utilisateur
            if "<@" in params[1] and ">" in params[1]:
                member = message.server.get_member(params[1].replace("<@", "").replace(">", ""))
            else:
                member = message.server.get_member_named(params[1])
            role = discord.utils.get(message.server.roles, name=" ".join(params[2:]))
            yield from self.remove_roles(member,
                                         role)  # cette ligne sert à retirer le rôle d'un utilisateur, son fonctionnement est quasi-identique à part qu'elle fait l'inverse (elle retire le rôle au lieu de l'ajouter)

        if command == "!roles" and trusted and not pm:  # Cette commande sert à lister les rôles sur le serveur
            for role in message.server.roles:  # cette ligne est une boucle et sert à mettre dans la variable role la liste des rôles du serveur avec message.server.roles
                yield from self.send_message(message.channel, role.id + " : " + role.name)

        if command == "!unban" and trusted and not pm:  # Cette commande sert à débannir un utilisateur
            if "<@" in params[1] and ">" in params[1]:
                id_user = message.server.get_member(params[1].replace("<@", "").replace(">", ""))
            else:
                id_user = message.server.get_member_named(params[1])
            yield from self.unban(message.server,
                                  id_user)  # pour débannir un utilisateur, il faut l'identifiant du serveur avec message.serveur et l'identifiant de l'utilisateur (voir !ban)

        if command == "!say" and trusted:  # Cette commande sert à envoyer un message sur un channel du serveur, le paramètre 1 doit être l'identifiant du channel et après, on doit mettre le message (exemple : !say 1234567890 Bonjour !)
            yield from self.send_message(self.get_channel(params[1]), " ".join(params[2:]))

        if command == "!say_user" and trusted:
            if params[2].lower() == params[2].upper():
                yield from self.send_message(self.get_server(params[1]).get_member(params[2]),
                                             " ".join(params[3:]))
            else:
                yield from self.send_message(
                    self.get_server(params[1]).get_member_named(params[2]),
                    " ".join(params[3:]))

        if command == "!status_game" and trusted:  # Cette commande sert à mettre que le self joue à un jeu, " ".join(params[1:]) est le nom du jeu.
            yield from self.change_presence(game=discord.Game(name=" ".join(params[1:])))

        if (
                command == "!topic" or command == "!topic_channel") and trusted and not pm:  # Ici, on a une commande qui change le sujet du channel où est tapée la commande
            yield from self.edit_channel(message.channel, topic=" ".join(params[1:]))

        if command == "!ver":  # Cette commande envoit la version du bot.
            yield from self.send_message(message.channel,
                                         "NextBot " + self.ver + " " + self.lang + " Discord.py " + discord.__version__)

        if command == "!viki" or command == "!vikidia":  # Cette commande sert à envoyer un lien vers un article de Vikidia.
            yield from self.send_message(message.channel,
                                         "https://" + params[1] + ".vikidia.org/wiki/" + "_".join(
                                             params[2:]))

        if command == "!wp" or command == "!wikipedia":  # Cette commande sert à envoyer un lien vers un article de Wikipédia.
            yield from self.send_message(message.channel,
                                         "https://" + params[
                                             1] + ".wikipedia.org/wiki/" + "_".join(
                                             params[2:]))

        if command == "!fetch_roles" and (trusted or role_trusted):
            for role in self.get_first_server().roles:
                data = {
                    'identifiant': str(role.id),
                    'name': role.name
                }
                response = requests.post("http://127.0.0.1:8000/bot/role/", data=data,
                                         auth=HTTPBasicAuth('admin', 'sysadmin')).json()
                print(response)

        if "il est cool " + user_bot.lower() in rep.lower():  # Ici, le bot peut répondre a des phrases, par exemple, en disant "Il est cool NextBot", le bot répondra "Merci du compliment, vous aussi vous êtes cool !".
            yield from self.send_message(message.channel,
                                         "Merci du compliment, vous aussi vous êtes cool ! :)")

        # Fin des commandes
        if not trusted and not role_trusted:
            content = message.content
            for word in blacklist:
                if content.find(word) > -1:
                    yield from self.delete_message(message)

    # A partir d'ici, vous pouvez personnaliser ce que fait le bot quand quelqu'un rejoint un serveur, quitte un serveur, etc...

    async def on_member_join(self, member):  # Fonction quand quelqu'un rejoint un serveur
        chan_name = "general"  # Nom du canal où le message est envoyé
        assert isinstance(member, discord.member.Member)
        await self.add_roles(member, self.get_default_role())

    async def on_server_role_create(self, role):
        data = {
            'identifiant': str(role.id),
            'name': role.name
        }
        response = requests.post("http://127.0.0.1:8000/bot/role/", data=data,
                                 auth=HTTPBasicAuth('admin', 'sysadmin')).json()

    async def on_server_role_delete(self, role):
        response = requests.delete("http://127.0.0.1:8000/bot/role/{}".format(str(role.id)),
                                   auth=HTTPBasicAuth('admin', 'sysadmin'))

    async def on_server_role_update(self, role_before, role_after):
        data = {
            'identifiant': str(role_after.id),
            'name': role_after.name
        }
        response = requests.patch("http://127.0.0.1:8000/bot/role/{}/".format(role_before.id),
                                  data=data,
                                  auth=HTTPBasicAuth('admin', 'sysadmin'))

    def run(self, *args, **kwargs):
        super().run(self.token)

    def get_first_server(self) -> discord.server.Server:
        """
        Renvoie le premier server où le bot est présent.
        :return: discord.server.Server
        """
        for i in self.servers:
            return i

    def get_default_role(self):
        response = requests.get("http://127.0.0.1:8000/bot/role/get_default/").json()
        print(response)
        for role in self.get_first_server().role_hierarchy:
            if role.id == response.get('identifiant'):
                print("Found")
                return role
        return None


bot = Shobot()
bot.run()
