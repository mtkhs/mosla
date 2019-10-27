import toml
from slacklib import SlackBot

if __name__ == "__main__":
    s = toml.load( open( 'setting.toml' ) )
    slackbot = SlackBot( s )
    slackbot.start()
