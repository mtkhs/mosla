from slacklib import SlackPlugin

class PingPong( SlackPlugin ):

    def on_message( self, user, channel, message ):
        if message.startswith( "<@" + self.userid() + ">" ):
            mention, text = message.split( " ", 2 )
            if text == "Ping!":
                self.send_message( channel, "<@" + user.id + "> Pong!" )
