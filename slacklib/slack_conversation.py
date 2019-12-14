
class SlackConversation():

    UNKNOWN = -1
    CHANNEL = 0
    GROUP = 1
    IM = 2

    def __init__( self, id ):
        self.id = id
        self.type = SlackConversation.UNKNOWN

    def is_channel( self ):
        return self.type == SlackConversation.CHANNEL

    def is_group( self ):
        return self.type == SlackConversation.GROUP

    def is_im( self ):
        return self.type == SlackConversation.IM
        