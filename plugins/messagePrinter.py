from slacklib import SlackPlugin

class MessagePrinter( SlackPlugin ):

    def on_message( self, user, channel, message ):
        print( message )
