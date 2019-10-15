import toml
import slack

from slacklib import SlackBot

SETTINGS = toml.load( open( 'settings.toml' ) )

if __name__ == "__main__":
    def on_open( **payload ):
        slackbot.on_open( payload )

    def on_message( **payload ):
        slackbot.on_message( payload )

    def on_member_joined_channel( **payload ):
        slackbot.on_channel_joined( payload )

    def on_member_left_channel( **payload ):
        slackbot.on_channel_left( payload )

    slackbot = SlackBot( SETTINGS )

    xoxp_token = SETTINGS[ 'slack' ][ 'xoxp_token' ]
    xoxb_token = SETTINGS[ 'slack' ][ 'xoxb_token' ]

    slackbot.web_client = slack.WebClient( token = xoxp_token )
    slackbot.rtm_client = slack.RTMClient( token = xoxb_token, connect_method = 'rtm.start' )
    
    slackbot.rtm_client.on( event = 'open', callback = on_open )
    slackbot.rtm_client.on( event = 'message', callback = on_message )
    slackbot.rtm_client.on( event = 'member_joined_channel', callback = on_member_joined_channel )
    slackbot.rtm_client.on( event = 'member_left_channel', callback = on_member_left_channel )
    
    slackbot.start()
