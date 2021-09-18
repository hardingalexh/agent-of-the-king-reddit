import os
import praw
import re
import requests

from dotenv import load_dotenv

load_dotenv()
cards = requests.get('https://www.arkhamdb.com/api/public/cards?encounter=1').json()

# subreddit response structure based on this tutorial
# https://praw.readthedocs.io/en/stable/tutorials/reply_bot.html

reddit = praw.Reddit(
    user_agent = os.getenv('USER_AGENT'),
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    username = os.getenv('USERNAME'),
    password = os.getenv('PASSWORD')
)

subreddit = reddit.subreddit('jaguarbottesting')
      
def respond_with_cards(comment, cardsearch):
    for search in cardsearch:
        levelSearch = re.search('(?<=\().+?(?=\))', search)
        if levelSearch:
            endpos = levelSearch.span()[0] - 1
            searchTerm = search[0:endpos].strip().lower()
            levelTerm = levelSearch.group()
            if levelTerm.lower() == 'u':
                matches = list(
                    filter(
                        lambda card: (
                            searchTerm.lower() in card.get('name', '').lower()) 
                            and (card.get('xp', 0) > 0), 
                            cards
                    )
                )
            elif int(levelTerm):
                matches = list(filter(lambda card: (searchTerm.lower() in card.get('name', '').lower()) and (card.get('xp', 0) == int(levelTerm)), cards))
        else:
            matches = list(filter(lambda card: search.lower() in card.get('name', '').lower(), cards))

    for match in matches:
        message = ""
        message += f"##{match.get('name')}"

        ## Faction, Type, Slot
        message += "\n\n"
        if match.get('faction') != "Mythos":
            message += f"Faction: _{match.get('faction_name')}_. "
        message += f"Type: _{match.get('type_name')}_"
        if match.get('slot', False):
            message += f" Slot: {match.get('slot')}"

        ## Trait(s)
        message += "\n\n"
        message += f"Traits: _{match.get('traits')}_"

        ## Test Icons
        processed_symbols = process_symbols(match)
        if processed_symbols != "":
            message += "\n\n"
            message += f"Test Icons: {processed_symbols}"

        ## Health, Sanity
        if (match.get('health') or match.get('sanity')) and match.get('type_code') != 'enemy':
            message += "\n\n"
            if(match.get('health')):
                message += f"Health: {str(match.get('health'))}. "
            if(match.get('sanity')):
                message += f"Sanity: {str(match.get('sanity'))}."
        
        ## Enemy Stats
        if match.get('type_code') == 'enemy':
            message += "\n\n"
            message += f"Fight: {str(match.get('enemy_fight'))}. Evade: {str(match.get('enemy_evade'))}."

            message += "\n\n"
            message += f"Health: {str(match.get('health'))}"
            if match.get('health_per_investigator', False):
                message += " Per Investigator"

            message += "\n\n"
            message += f"Damage: {str(match.get('enemy_damage'))}. Horror: {str(match.get('enemy_horror'))}"

            if match.get('victory', False):
                message += "\n\n"
                message += f"Victory {match.get('victory')}"

        ## Card Text
        message += "\n\n"
        message += f"{process_text(match.get('text'))}"

        ## Card Image
        if match.get('imagesrc'):
            message +="\n\n"
            message += f"[Card Image](https://www.arkhamdb.com{match.get('imagesrc')})"

        ## Card URL
        message += "\n\n"
        message += f"[View card on ArkhamDB]({match.get('url')})"

        ## Horizontal Rule
        message +="\n\n"
        message += "***"

        ## Bot Disclaimer
        message += "\n\n"
        message += "^(I am a bot. This is a test.)"

        comment.reply(message)

##########################################################
# Reprocesses ArkhamDB markdown to reddit markdown       #
##########################################################
def process_text(text):
    text = text.replace("[[", '**')
    text = text.replace("]]", '**')

    text = text.replace("<b>", "**")
    text = text.replace("</b>", "**")

    text = text.replace("<i>", "_")
    text = text.replace("</i>", "_")

    text = text.replace("\n", "\n\n")
    return text

##########################################################
# Creates a string of test icons for a given player card #
##########################################################
def process_symbols(card):
    stats = ['Willpower', 'Intellect', 'Combat', 'Agility']
    message = ""
    for stat in stats:
        if(card.get(f'skill_{stat.lower()}')):
            message += f" {stat} x{str(card.get('skill_' + stat.lower()))}"
    return message

def main():
    checks = 0
    for comment in subreddit.stream.comments():
        already_replied = False
        if comment.author.name == reddit.user.me().name:
            already_replied = True
        comment.refresh() # fetches comment replies
        for reply in comment.replies:
            if reply.author.name == reddit.user.me().name:
                already_replied = True
        if not already_replied:
            cardsearch = re.findall('(?<=\[\[).+?(?=\]\])', comment.body)
            if len(cardsearch):
                respond_with_cards(comment, cardsearch)

if __name__ == "__main__":
    main()