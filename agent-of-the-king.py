import os
import praw

from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    user_agent = os.getenv('USER_AGENT'),
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    username = os.getenv('USERNAME'),
    password = os.getenv('PASSWORD')\
)
