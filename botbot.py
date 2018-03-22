import os
import time
import re
from slackclient import SlackClient
from googleapiclient.discovery import build

# instantiate Slack client
slack_client = SlackClient('xoxb-331270929271-BTsxyzdGwyX8GSisCgDi0dol')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

my_api_key = "AIzaSyDOJ7N0pYMfxDDcDPt8hSJrA5_SiF28vN0"
my_cse_id = "017409893909469164746:aclwedjs-ui"

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "busca"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

"""
    Google search library which uses a custom search engine to return results from Wikipedia.
"""

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "No se a que te refieres. Prueba *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        search = command.replace('busca','')
        results = google_search(search, my_api_key, my_cse_id, num=2)
        
        response = results[0]["snippet"]

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")