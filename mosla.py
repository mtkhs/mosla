import toml
from slacklib import SlackBot

SETTINGS = toml.load( open( 'settings.toml' ) )

if __name__ == "__main__":
    slack = SlackBot( SETTINGS[ 'slack' ][ 'api_token' ], SETTINGS[ 'bot' ][ 'plugins_dir' ], SETTINGS[ 'bot' ][ 'rtm_interval' ] )
    slack.start()
