from slacklib import SlackPlugin
import datetime

class Welcome( SlackPlugin ):

    def bot_construct( self ):
        pass

    def on_joined( self, channel, user ):
        now = datetime.datetime.now()
        if( 9 <= now.hour and now.hour < 18 ):
            self.send_message( channel, 'Hello, <@' + user.id + '>!' )
        else:
            self.send_message( channel, 'Welcome, <@' + user.id + '>!' )
