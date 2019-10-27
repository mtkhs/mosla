from slacklib import SlackPlugin
import datetime

class Kicker( SlackPlugin ):

    def bot_construct( self ):
        pass

    def on_message( self, channel, user, message ):
        if( message == '!kickme' ):
            print( 'send_kick' )
            self.send_kick( channel, user )
