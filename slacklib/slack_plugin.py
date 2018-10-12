
class SlackPlugin():

    def __init__( self, bot, name ):
        self.bot = bot
        self.name = name

    def is_mention_to_me( self, message ):
        return message.startswith( "<@" + self.bot.self_id() + ">" )

    def is_mention_message( self, message ):
        return message.startswith( "<@" )

    def parse_mention_text( self, text ):
        user, message = text.split( " ", 1 )
        user = self.bot.users_list[ user[ 2 : -1 ] ]
        return ( user, message )

    def send_message( self, channel, message ):
        self.bot.send_message( channel, message )

    def send_mention_message( self, channel, user, message ):
        self.bot.send_mention_message( channel, user, message )

    # abstract methods

    def on_server_connect( self ):
        pass

    def on_message( self, user, channel, message ):
        pass

    def on_message_changed( self, channel, user, message, prev_user, prev_message ):
        pass

    def on_joined( self, channel, user ):
        pass

    def on_left( self, channel, user ):
        pass

    def on_raw( self, line ):
        pass
