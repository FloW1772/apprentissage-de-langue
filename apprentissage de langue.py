import discord
import random
from discord.ext import commands

# Remplacez "VOTRE_TOKEN_ICI" par le jeton d'authentification de votre bot.
TOKEN = 'VOTRE_TOKEN_ICI'
# Préfixe des commandes du bot.
PREFIX = '!'

# Liste des langues supportées (ajoutez-en plus si nécessaire)
LANGUES = ['fr', 'en']

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
        self.scores = {}

    def ajouter_score(self, utilisateur):
        if utilisateur not in self.scores:
            self.scores[utilisateur] = 0
        self.scores[utilisateur] += 1

    def obtenir_score(self, utilisateur):
        return self.scores.get(utilisateur, 0)

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
                self.score_manager.ajouter_score(user_response.author)
                await ctx.send(f'Bravo ! La réponse est correcte : {question["reponse"]}')
            else:
                await ctx.send(f'Désolé, la réponse est incorrecte. La réponse était : {question["reponse"]}')
        except asyncio.TimeoutError:
            await ctx.send(f'Désolé, le temps est écoulé. La réponse était : {question["reponse"]}')

    @commands.command()
    async def score(self, ctx):
        score = self.score_manager.obtenir_score(ctx.author)
        await ctx.send(f'Votre score est de {score} point(s).')

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
