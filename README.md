# agent-of-the-king-reddit
An arkhamdb.com card gathering bot for the r/arkhamhorrorlcg subreddit

## Usage
This bot listens to all comments on the [r/arkhamhorrorlcg subreddit](https://www.reddit.com/r/arkhamhorrorlcg). It has the following features:

### Card Embeds
To have the bot respond to your comment with cards, include the name of your card between double brackets. For example, including `[[ancient evils]]` will return [Ancient Evils](https://arkhamdb.com/card/01166). Some facts about the card search functionality:

* Search is not case sensitive
* Search will return every card that matches a substring:
    * for example, searching `[[derringer]]` will return both the .41 Derringer and the .18 Derringer
* Searches can optionally include a level in parentheses
    * for example, `[[.41 Derringer]]` will return both the level 0 and the level 2, but `[[.41 derringer (0)]]` will only return the level 0 version
* Multiple embeds per post will return multiple comments
    * For example, commenting "you should consider either the `[[.41 derringer (2)]]` or the `[[chicago typewriter]]` will return comments with each card embedded

### Deck Embeds
Any comment that includes a link to a valid arkhamdb deck or decklist will receive a reply with a formatted version of that deck's contents. Valid links include decks (for example `https://arkhamdb.com/deck/view/1514964`) and decklists (`https://arkhamdb.com/decklist/view/29846/nun-with-a-gun-post-play-1.0`).

## Development

### Setup
This bot requires Python 3.6+. In order to set it up for development, use these steps:
* Clone the repository
* Create a virtual environment using your venv of choice
    * For example, use basic [python 3 venvs](https://docs.python.org/3/library/venv.html)
    * From the repository root, run `python3 -m venv .venv`
    * then run `. .venv/bin/activate`
* Install dependencies using pip `pip install -r requirements.txt`
* Create a reddit application [in your account preferences](https://ssl.reddit.com/prefs/apps/)
* Add your bot's credentials
    * `cp .env.example .env`
    * edit the `.env` file to include your bot account's credentials
* Run the application `python3 agent-of-the-king.py`

### Docker
This repository includes a dockerfile for running the application in a container. In order to build a new version and deploy it, run the following:
* `docker build -t agent-of-the-king-reddit ./`
* `docker run --name agent-of-the-king-reddit --restart always -d agent-of-the-king-reddit`
