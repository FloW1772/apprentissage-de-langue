import discord
import random

# Remplacez "VOTRE_TOKEN_ICI" par le jeton d'authentification de votre bot.
TOKEN = 'VOTRE_TOKEN_ICI'
# Préfixe des commandes du bot.
PREFIX = '!'

# Créez un client Discord
client = discord.Client()

# Exercices par langue (ajoutez-en plus si nécessaire)
exercices = {
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
        # Add more exercises here
    ]
}

# Classe pour gérer les exercices et les scores des utilisateurs
class LangueBot:
    def __init__(self):
        self.scores = {}
    
    def choisir_question(self, langue):
        questions = exercices.get(langue, [])
        return random.choice(questions) if questions else None
    
    def verifier_reponse(self, langue, question, reponse_utilisateur):
        return reponse_utilisateur.lower().strip() == question['reponse'].lower().strip()

    def ajouter_score(self, utilisateur):
        if utilisateur not in self.scores:
            self.scores[utilisateur] = 0
        self.scores[utilisateur] += 1

    def obtenir_score(self, utilisateur):
        return self.scores.get(utilisateur, 0)

# Créez une instance du bot d'apprentissage des langues
langue_bot = LangueBot()

# Événement déclenché lorsque le bot est prêt à fonctionner
@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user}')

# Événement déclenché lorsqu'un message est envoyé sur le serveur
@client.event
async def on_message(message):
    # Vérifiez si le message provient du bot lui-même pour éviter les boucles infinies
    if message.author == client.user:
        return

    # Vérifiez si le message commence par le préfixe
    if message.content.startswith(PREFIX):
        # Récupérez la commande et les arguments
        command, *args = message.content[len(PREFIX):].lower().strip().split()

        # Commande pour commencer un quiz
        if command == 'quiz':
            # Vérifiez si une langue est spécifiée, sinon utilisez la langue par défaut (français)
            langue = args[0] if args and args[0] in exercices else 'fr'

            # Choisissez une question aléatoire
            question = langue_bot.choisir_question(langue)
            if not question:
                await message.channel.send(f'Aucun exercice disponible pour la langue {langue}.')
                return

            # Envoyez la question à l'utilisateur
            await message.channel.send(f'Quiz ({langue}) : {question["question"]}')

            # Fonction pour vérifier la réponse de l'utilisateur
            def check(m):
                return m.author == message.author

            try:
                # Attendre la réponse de l'utilisateur pendant 10 secondes
                user_response = await client.wait_for('message', timeout=10.0, check=check)
                if langue_bot.verifier_reponse(langue, question, user_response.content):
                    langue_bot.ajouter_score(user_response.author)
                    await message.channel.send(f'Bravo ! La réponse est correcte : {question["reponse"]}')
                else:
                    await message.channel.send(f'Désolé, la réponse est incorrecte. La réponse était : {question["reponse"]}')
            except asyncio.TimeoutError:
                await message.channel.send(f'Désolé, le temps est écoulé. La réponse était : {question["reponse"]}')

        # Commande pour afficher le score de l'utilisateur
        elif command == 'score':
            utilisateur = message.author
            score = langue_bot.obtenir_score(utilisateur)
            await message.channel.send(f'Votre score est de {score} point(s).')

# Connectez-vous au serveur Discord avec le jeton du bot
client.run(TOKEN)
