from slacklib import SlackPlugin

class RawPrinter( SlackPlugin ):

    def on_raw( self, line ):
        print( line )
