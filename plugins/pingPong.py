from slacklib import SlackPlugin

class PingPong( SlackPlugin ):

    def bot_construct( self ):
        self.ping_text = self.setting[ 'ping_text' ]
        self.pong_text = self.setting[ 'pong_text' ]

    def on_message( self, channel, user, message ):
        if user.id == self.bot.self_id(): # ignore own message
            return
        if self.is_mention_to_me( message ):
            to_user, message = self.parse_mention_text( message )
            if message == self.ping_text:
                self.send_mention_message( channel, user, self.pong_text )
