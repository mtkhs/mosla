from slacklib import SlackPlugin

class ServerConnectedNotifier( SlackPlugin ):

    def on_server_connected( self ):
        print( __name__ + ": Server Connected!" )
