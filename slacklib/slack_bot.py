import os
import importlib
from slackclient import SlackClient
import time
from slacklib import SlackUser
from slacklib import SlackPlugin
from slacklib import SlackChannel

class SlackBot():

    def __init__( self, token, plugins_path = "plugins", rtm_interval = 1 ):
        self.sc = SlackClient( token )
        self.plugins_path = plugins_path
        self.rtm_interval = rtm_interval
        self.plugin_modules = []
        self.plugin_classes = []
        self.plugin_instances = []
        self.users_list = {} # [ 'id' ] => SlackUser
        self.channels_list = {}

# plugin loader

    def load_plugins( self ):
        plugins_dir = os.listdir( self.plugins_path )
        current_dir = os.path.dirname( os.path.abspath( __file__ ) )
        for filename in plugins_dir:
            if filename.endswith('.py'):
                if filename == "__init__.py":
                    continue
                klassName = os.path.splitext( filename )[ 0 ]
                klassName = klassName[ 0 ].upper() + klassName[ 1: ]
                modulePath =  self.plugins_path + '/' + filename
                cpath = os.path.splitext( modulePath )[ 0 ].replace( os.path.sep, '.' )
                try:
                    mod = importlib.import_module( cpath )
                    self.plugin_modules.append( mod )
                    klass = getattr( mod, klassName )
                    self.plugin_classes.append( klass )
                    self.plugin_instances.append( klass( self, klassName ) )
                except ModuleNotFoundError:
                    print('Module not found')
                except AttributeError:
                    print('Method not found')

    def unload_plugins( self ):
        pass

    def reload_plugins( self ):
        unload_plugins()
        load_plugins()

    # bot information

    def self_info( self ):
        return self.sc.server.login_data[ 'self' ]

    def self_id( self ):
        return self.self_info()[ 'id' ]

    def self_name( self ):
        return self.self_info()[ 'name' ]

    def update_users_list( self ):
        users = self.sc.server.login_data[ 'users' ]
        for user in users:
            self.users_list[ user[ 'id' ] ] = SlackUser( user[ 'id' ], user[ 'name' ], user[ 'real_name' ], user[ 'profile' ][ 'email' ] )

    def update_channels_list( self ):
        channels = self.sc.server.login_data[ 'channels' ]
        for channel in channels:
            self.channels_list[ channel[ 'id' ] ] = SlackChannel( channel[ 'id' ], channel[ 'name' ] )

    # plugin commands

    def send_message( self, channel, message ):
        self.sc.api_call( "chat.postMessage", channel = channel, text = message, as_user = True )

    def send_mention_message( self, channel, user, message ):
        mention_message = "<@" + user.id + "> " + message
        self.sc.api_call( "chat.postMessage", channel = channel, text = mention_message, as_user = True )

    # plugin events

    def on_message( self, user, channel, message ):
        for plugin in self.plugin_instances:
            plugin.on_message( user, channel, message )

    def on_message_changed( self, channel, user, message, prev_user, prev_message ):
        for plugin in self.plugin_instances:
            plugin.on_message_changed( channel, user, message, prev_user, prev_message )

    def on_joined( self, channel, user ):
        for plugin in self.plugin_instances:
            plugin.on_joined( channel, user )

    def on_left( self, channel, user ):
        for plugin in self.plugin_instances:
            plugin.on_left( channel, user )

    def on_server_connect( self ):
        for plugin in self.plugin_instances:
            plugin.on_server_connect()

    def on_raw( self, line ):
        for plugin in self.plugin_instances:
            plugin.on_raw( line )

    # process slack events

    def process_message_changed( self, item ):
        channel = self.channels_list[ item[ 'channel' ] ]
        user = self.users_list[ item[ 'message' ][ 'user' ] ]
        message = item[ 'message' ][ 'text' ]
        prev_user = item[ 'previous_message' ][ 'user' ]
        prev_message = item[ 'previous_message' ][ 'text' ]
#        if user.id != self.self_id(): # ignore own message
        self.on_message_changed( channel, user, message, prev_user, prev_message )

    def process_message( self, item ):
        if 'subtype' in item:
            if item[ 'subtype' ] == 'message_changed':
                self.process_message_changed( item )
        else:
            user = self.users_list[ item[ 'user' ] ]
            channel = self.channels_list[ item[ 'channel' ] ]
            message = item[ 'text' ]
#            if user.id != self.self_id(): # ignore own message
            self.on_message( user, channel, message )

    def process_item( self, item ):
        if item[ 'type' ] == 'message':
            self.process_message( item )
        elif item[ 'type' ] == 'member_joined_channel':
            user = self.users_list[ item[ 'user' ] ]
            channel = self.channels_list[ item[ 'channel' ] ]
            self.on_joined( channel, user )
        elif item[ 'type' ] == 'member_left_channel':
            user = self.users_list[ item[ 'user' ] ]
            channel = self.channels_list[ item[ 'channel' ] ]
            self.on_left( channel, user )

    def process_line( self, line ):
        for item in line:
            self.process_item( item )

    # process slack rtm

    def rtm_read_loop( self ):
        while self.sc.server.connected:
            line = self.sc.rtm_read()
            if 0 < len( line ):
                self.process_line( line )
                self.on_raw( line )
            time.sleep( self.rtm_interval )

    def start( self ):
        self.load_plugins()
        if self.sc.rtm_connect():
            self.update_users_list()
            self.update_channels_list()
            self.on_server_connect()
            self.rtm_read_loop()
        else:
            print( "Connection Failed" )
