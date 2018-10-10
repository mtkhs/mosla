
class SlackPlugin():

    def __init__( self, slackClient, name ):
        self.sc = slackClient
        self.name = name

    def self_info( self ):
        return self.sc.server.login_data[ 'self' ]

    def userid( self ):
        return self.self_info()[ 'id' ]

    def username( self ):
        return self.self_info()[ 'name' ]

    def on_server_connected( self ):
        pass

    def on_message( self, user, channel, message ):
        pass

    def on_raw( self, line ):
        pass

    def send_message( self, channel, message ):
        self.sc.api_call( "chat.postMessage", channel = channel, text = message, as_user = True )

