from slacklib import SlackConversation

class SlackGroup( SlackConversation ):

    def __init__( self, channel ):
        super().__init__( channel[ 'id' ] )
        self.data = channel
        self.type = SlackConversation.GROUP
