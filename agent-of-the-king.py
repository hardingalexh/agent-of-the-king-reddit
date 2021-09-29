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

subreddit = reddit.subreddit(os.getenv('SUBREDDIT'))

footer = f"\n\n***\n\n^(I am a bot. This message was posted automatically. For more information or to log an issues, check me out on) [github](https://github.com/hardingalexh/agent-of-the-king-reddit)"

##########################################################
# For a given search string, find all matching cards and #
# respond once with each card                            #
##########################################################     
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
        message += footer
        
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

##########################################################
# Embeds decks if a valid arkhamdb deck link is detected #
##########################################################
def respond_with_deck(comment):
    content = comment.body.lower()
    # parse message to get deck id and type (decklist or deck)
    deckId = None
    deckType = None
    if "arkhamdb.com/deck/view/" in content:
        deckId = re.search('(?<=arkhamdb\.com\/deck\/view\/).+?(?=\b|$|\s)', content)
        deckType = 'deck'
    if "https://arkhamdb.com/decklist/" in content:
        deckId = re.search('(?<=arkhamdb\.com\/decklist\/view\/).+?(?=\b|$|\s)', content)
        deckType = 'decklist'

    
    if deckId:
        import pdb; pdb.set_trace()
        # get deck from arkhamdb api
        deckId = deckId.group()
        ## hacky hedge for when regex doesn't work the way I expect it to
        deckId = deckId.split('/')[0]
        if deckType == 'deck':
            apiString = 'https://arkhamdb.com/api/public/deck/' + deckId
        if deckType == 'decklist':
            apiString = 'https://arkhamdb.com/api/public/decklist/' + deckId
        deckJson = requests.get(apiString).json()

        # create initial message
        
        message = ""
        # Use gator/deck name as header
        gator = list(filter(lambda card: card.get('code', 0) == deckJson.get('investigator_code', None), cards))[0]
        message += f"#{gator.get('name', '')}: {deckJson.get('name', '')} {deckJson.get('version', '')}"


        ## Add link back to arkhamdb
        message += "\n\n"
        if deckType == 'deck':
            message += f'[View on Arkhamdb](https://arkhamdb.com/deck/view/{deckId})'
        if (deckType == 'decklist'):
            message += f'[View on Arkhamdb](https://arkhamdb.com/decklist/view{deckId})'
        
        ## Horizontal Rule
        message +="\n\n"
        message += "***"

        ## get all cards used in deck
        deckCards = list(filter(lambda card: card.get('code', '') in deckJson.get('slots', {}).keys(), cards))

        categories = ['Asset', 'Permanent', 'Event', 'Skill', 'Treachery', 'Enemy']
        for category in categories:
            ## handle category codes
            if(category == 'Permanent'):
                categoryCards = list(filter(lambda card: card.get('permanent', False) == True, deckCards))
            else:
                categoryCards = list(filter(lambda card: card.get('type_code', '') == category.lower() and card.get('permanent', False) == False, deckCards))
            if(category == 'Treachery'):
                message += '\n\n **Treacheries:**'
            elif(category == 'Enemy'):
                message += '\n\n **Enemies:**'
            else:
                message += f'\n\n **{category}s:**'
            # handle asset slots
            if category == 'Asset':
                def slotFilter(e):
                    return e.get('slot', 'zzzzzz')
                categoryCards.sort(key=slotFilter)
                slots = []

            for card in categoryCards:
                cardString = f"{deckJson.get('slots')[card.get('code')]} x "
                cardString += f"[{card.get('name', '')}]({card.get('url', '')})"
                if card.get('xp', 0) > 0:
                    cardString += ' (' + str(card.get('xp', 0)) + ')'

                if category == 'Asset' and card.get('slot', '') not in slots:
                    message += '\n\n' + card.get('slot', 'Other') + ':'
                    slots.append(card.get('slot', ''))
                message += '\n\n' + cardString
            message += '\n\n'
        

        ## footer
        message += footer

        comment.reply(message)

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

            # search for cards
            cardsearch = re.findall('(?<=\[\[).+?(?=\]\])', comment.body)
            if len(cardsearch):
                respond_with_cards(comment, cardsearch)
            
            # search for arkhamdb decks
            if "arkhamdb.com/deck/view/" in comment.body.lower() or 'arkhamdb.com/decklist/view/' in comment.body.lower():
                respond_with_deck(comment)

if __name__ == "__main__":
    main()