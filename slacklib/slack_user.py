
class SlackUser():

    def __init__( self, user ):
        self.data = user
        self.id = user[ 'id' ]
        self.team_id = user[ 'team_id' ]
        self.name = user[ 'name' ]
        self.profile = user[ 'profile' ]
        self.is_bot = user[ 'is_bot' ]
