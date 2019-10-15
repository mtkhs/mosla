
class SlackChannel():

    def __init__( self, channel ):
        self.data = channel
        self.id = channel[ 'id' ]
        self.name = channel[ 'name' ]
        self.is_member = channel[ 'is_member' ]
