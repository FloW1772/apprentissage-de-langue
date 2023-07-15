import discord
import random
import sqlite3
from discord.ext import commands

# Remplacez "VOTRE_TOKEN_ICI" par le jeton d'authentification de votre bot.
TOKEN = 'VOTRE_TOKEN_ICI'
# Préfixe des commandes du bot.
PREFIX = '!'

# Liste des langues supportées (ajoutez-en plus si nécessaire)
LANGUES = ['fr', 'en', 'es', 'de', 'it']

# Classe pour gérer les exercices
class LangueBot:
    def __init__(self):
        self.exercices = {
            'fr': [
                {
                    'question': 'Quelle est la capitale de la France ?',
                    'reponse': 'Paris'
                },
                {
                    'question': 'Comment dit-on "bonjour" en français ?',
                    'reponse': 'Bonjour'
                },
                {
                    'question': 'Quel est le symbole chimique de l\'hydrogène ?',
                    'reponse': 'H'
                }
                # Ajoutez plus d'exercices ici
            ],
            'en': [
                {
                    'question': 'What is the capital of the United States?',
                    'reponse': 'Washington, D.C.'
                },
                {
                    'question': 'How do you say "thank you" in English?',
                    'reponse': 'Thank you'
                },
                {
                    'question': 'What is the chemical symbol for oxygen?',
                    'reponse': 'O'
                }
                # Ajoutez plus d'exercices ici
            ],
            'es': [
                {
                    'question': '¿Cuál es la capital de España?',
                    'reponse': 'Madrid'
                },
                {
                    'question': '¿Cómo se dice "hola" en español?',
                    'reponse': 'Hola'
                },
                {
                    'question': '¿Cuál es el símbolo químico del hidrógeno?',
                    'reponse': 'H'
                }
                # Ajoutez plus d'exercices ici
            ],
            'de': [
                {
                    'question': 'Was ist die Hauptstadt von Deutschland?',
                    'reponse': 'Berlin'
                },
                {
                    'question': 'Wie sagt man "Hallo" auf Deutsch?',
                    'reponse': 'Hallo'
                },
                {
                    'question': 'Was ist das chemische Symbol für Wasserstoff?',
                    'reponse': 'H'
                }
                # Ajoutez plus d'exercices ici
            ],
            'it': [
                {
                    'question': 'Qual è la capitale dell\'Italia?',
                    'reponse': 'Roma'
                },
                {
                    'question': 'Come si dice "ciao" in italiano?',
                    'reponse': 'Ciao'
                },
                {
                    'question': 'Quale è il simbolo chimico dell\'idrogeno?',
                    'reponse': 'H'
                }
                # Ajoutez plus d'exercices ici
            ]
        }

    def choisir_question(self, langue):
        questions = self.exercices.get(langue, [])
        return random.choice(questions) if questions else None

    def verifier_reponse(self, langue, question, reponse_utilisateur):
        return reponse_utilisateur.lower().strip() == question['reponse'].lower().strip()

# Classe pour gérer les scores
class ScoreManager:
    def __init__(self):
        self.conn = sqlite3.connect('scores.db')
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER)')

    def ajouter_score(self, utilisateur, score):
        with self.conn:
            self.conn.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', (utilisateur.id, score))

    def obtenir_score(self, utilisateur):
        with self.conn:
            cursor = self.conn.execute('SELECT SUM(score) FROM scores WHERE user_id = ?', (utilisateur.id,))
            score = cursor.fetchone()[0]
            return score if score else 0

    def obtenir_meilleurs_scores(self, limit=10):
        with self.conn:
            cursor = self.conn.execute('SELECT user_id, SUM(score) as total_score FROM scores GROUP BY user_id ORDER BY total_score DESC LIMIT ?', (limit,))
            return cursor.fetchall()

# Classe principale du bot
class LangueBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.langue_bot = LangueBot()
        self.score_manager = ScoreManager()

    @commands.command()
    async def quiz(self, ctx, langue='fr'):
        # Vérifiez si la langue est supportée
        if langue not in LANGUES:
            await ctx.send(f'Langue non supportée. Les langues disponibles sont : {", ".join(LANGUES)}')
            return

        # Choisissez une question aléatoire
        question = self.langue_bot.choisir_question(langue)
        if not question:
            await ctx.send(f'Aucun exercice disponible pour la langue {langue}.')
            return

        # Envoyez la question à l'utilisateur
        await ctx.send(f'Quiz ({langue}) : {question["question"]}')

        def check(m):
            return m.author == ctx.author

        try:
            user_response = await self.bot.wait_for('message', timeout=10.0, check=check)
            if self.langue_bot.verifier_reponse(langue, question, user_response.content):
                self.score_manager.ajouter_score(user_response.author, 1)
                await ctx.send(f'Bravo ! La réponse est correcte : {question["reponse"]}')
            else:
                await ctx.send(f'Désolé, la réponse est incorrecte. La réponse était : {question["reponse"]}')
        except asyncio.TimeoutError:
            await ctx.send(f'Désolé, le temps est écoulé. La réponse était : {question["reponse"]}')

    @commands.command()
    async def score(self, ctx):
        score = self.score_manager.obtenir_score(ctx.author)
        await ctx.send(f'Votre score est de {score} point(s).')

    @commands.command()
    async def top(self, ctx, limit=10):
        meilleurs_scores = self.score_manager.obtenir_meilleurs_scores(limit)
        if meilleurs_scores:
            message = "Top scores :\n"
            for i, (user_id, score) in enumerate(meilleurs_scores, start=1):
                user = ctx.guild.get_member(user_id)
                user_name = user.name if user else f"Utilisateur inconnu ({user_id})"
                message += f"{i}. {user_name} - {score} point(s)\n"
            await ctx.send(message)
        else:
            await ctx.send("Aucun score enregistré.")

# Créez une instance du bot avec le préfixe défini
bot = commands.Bot(command_prefix=PREFIX)
# Ajoutez le Cog LangueBotCog au bot
bot.add_cog(LangueBotCog(bot))

# Événement déclenché lorsque le bot est prêt à fonctionner
@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

# Connectez-vous au serveur Discord avec le jeton du bot
bot.run(TOKEN)
