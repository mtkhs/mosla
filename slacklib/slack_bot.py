import os
import importlib
from slackclient import SlackClient
import time
from slacklib.slack_user import SlackUser
from slacklib.slack_plugin import SlackPlugin
from slacklib.slack_channel import SlackChannel

class SlackBot():

    def __init__( self, token, plugins_path = "plugins" ):
        self.sc = SlackClient( token )
        self.plugins_path = plugins_path
        self.plugin_modules = []
        self.plugin_classes = []
        self.plugin_instances = []
        self.users_list = {} # [ 'id' ] => SlackUser
        self.channels_list = {}

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
                    self.plugin_instances.append( klass( self.sc, klassName ) )
                except ModuleNotFoundError:
                    print('Module not found')
                except AttributeError:
                    print('Method not found')

    def unload_plugins( self ):
        pass

    def reload_plugins( self ):
        unload_plugins()
        load_plugins()

    def update_users_list( self ):
        users = self.sc.server.login_data[ 'users' ]
        for user in users:
            self.users_list[ user[ 'id' ] ] = SlackUser( user[ 'id' ], user[ 'name' ], user[ 'real_name' ], user[ 'profile' ][ 'email' ] )

    def update_channels_list( self ):
        channels = self.sc.server.login_data[ 'channels' ]
        for channel in channels:
            self.channels_list[ channel[ 'id' ] ] = SlackChannel( channel[ 'id' ], channel[ 'name' ] )

    def on_message( self, user, channel, message ):
        for plugin in self.plugin_instances:
            plugin.on_message( user, channel, message )

    def on_message_changed( self, channel, user, message, prev_user, prev_message ):
        pass

    def on_server_connected( self ):
        for plugin in self.plugin_instances:
            plugin.on_server_connected()

    def on_raw( self, line ):
        for plugin in self.plugin_instances:
            plugin.on_raw( line )

    def start( self ):
        self.load_plugins()
        if self.sc.rtm_connect():
            self.update_users_list()
            self.update_channels_list()
            self.on_server_connected()
            while self.sc.server.connected is True:
                line = self.sc.rtm_read() # JSON format
                if 0 < len( line ):
                    self.on_raw( line )
                    for item in line:
                        type = item[ 'type' ]
                        if type == 'message':
                            if 'subtype' in item:
                                if item[ 'subtype' ] == 'message_changed':
                                    channel = item[ 'channel' ]
                                    user = self.users_list[ item[ 'message' ][ 'user' ] ]
                                    message = item[ 'message' ][ 'text' ]
                                    prev_user = item[ 'previous_message' ][ 'user' ]
                                    prev_message = item[ 'previous_message' ][ 'text' ]
                                    self.on_message_changed( channel, user, message, prev_user, prev_message )
                            else:
                                # Normal message
                                user = self.users_list[ item[ 'user' ] ]
                                channel = item[ 'channel' ]
                                message = item[ 'text' ]
                                self.on_message( user, channel, message )

                time.sleep(0.1)
        else:
            print( "Connection Failed" )
