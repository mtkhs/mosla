from slacklib import SlackPlugin

class PingPong( SlackPlugin ):

    def on_message( self, user, channel, message ):
        if user.id == self.bot.self_id(): # ignore own message
            return
        if self.is_mention_to_me( message ):
            to_user, message = self.parse_mention_text( message )
            if message == "Ping!":
                self.send_mention_message( channel, user, "Pong!" )
