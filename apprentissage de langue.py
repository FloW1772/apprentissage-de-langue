import discord
import random

# Remplacez "VOTRE_TOKEN_ICI" par le jeton d'authentification de votre bot.
TOKEN = 'VOTRE_TOKEN_ICI'
# Préfixe des commandes du bot.
PREFIX = '!'

# Créez un client Discord
client = discord.Client()

# Liste des questions pour les quiz
questions = [
    {
        'question': 'Quelle est la capitale de la France ?',
        'reponse': 'Paris'
    },
    {
        'question': 'Comment dit-on "bonjour" en anglais ?',
        'reponse': 'Hello'
    },
    # Ajoutez plus de questions ici
]

# Fonction pour choisir une question aléatoire
def choisir_question():
    return random.choice(questions)

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
        command = message.content[len(PREFIX):].lower().strip()

        # Commande pour commencer un quiz
        if command == 'quiz':
            # Choisissez une question aléatoire
            question_data = choisir_question()
            question = question_data['question']
            reponse = question_data['reponse']

            # Envoyez la question à l'utilisateur
            await message.channel.send(f'Quiz : {question}')

            # Fonction pour vérifier la réponse de l'utilisateur
            def check(m):
                return m.author == message.author and m.content.lower().strip() == reponse.lower()

            try:
                # Attendre la réponse de l'utilisateur pendant 10 secondes
                user_response = await client.wait_for('message', timeout=10.0, check=check)
                await message.channel.send(f'Bravo ! La réponse est correcte : {reponse}')
            except asyncio.TimeoutError:
                await message.channel.send('Désolé, le temps est écoulé. La réponse était : {reponse}')

# Connectez-vous au serveur Discord avec le jeton du bot
client.run(TOKEN)
