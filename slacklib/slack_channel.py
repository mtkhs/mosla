from slacklib import SlackConversation

class SlackChannel( SlackConversation ):

    def __init__( self, channel ):
        super().__init__( channel[ 'id' ] )
        self.data = channel
        self.name = channel[ 'name' ]
        self.type = SlackConversation.CHANNEL
