from slacklib import SlackConversation

class SlackIM( SlackConversation ):

    def __init__( self, channel ):
        super().__init__( channel[ 'id' ] )
        self.data = channel
        self.user = channel[ 'user' ]
        self.type = SlackConversation.IM
