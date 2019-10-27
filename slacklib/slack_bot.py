import os
import importlib
import time
import slack
import asyncio
from slacklib import SlackUser
from slacklib import SlackPlugin
from slacklib import SlackChannel

class SlackBot():

    def __init__( self, setting ):
        xoxp_token = setting[ 'slack' ][ 'xoxp_token' ]
        xoxb_token = setting[ 'slack' ][ 'xoxb_token' ]
        self._web_client = slack.WebClient( token = xoxp_token )
        self._rtm_client = slack.RTMClient( token = xoxb_token, connect_method = 'rtm.start' )
#        self._rtm_loop = asyncio.new_event_loop()
#        asyncio.set_event_loop( self._rtm_loop )
#        self._rtm_client = slack.RTMClient( token = xoxb_token, connect_method = 'rtm.start', run_async = True, loop = self._rtm_loop )
        self.plugins_setting = setting[ 'plugins' ]
        self.plugins_path = setting[ 'bot' ][ 'plugins_dir' ]
        self.plugin_modules = []
        self.plugin_classes = []
        self.plugin_instances = []
        self._self = None
        self._team = None
        self._users_list = {} # [ 'id' ] => SlackUser
        self._channels_list = {}
        self._data = None

    def _get_rtm_client( self ):
        return self._rtm_client

    def _set_rtm_client( self, rc ):
        self._rtm_client = rc

    rtm_client = property( _get_rtm_client, _set_rtm_client )

    def _get_web_client( self ):
        return self._web_client

    def _set_web_client( self, rc ):
        self._web_client = rc

    web_client = property( _get_web_client, _set_web_client )

    # plugin loader

    def load_plugins( self ):
        for ps in self.plugins_setting:
            mod = importlib.import_module( ps[ 'module' ] )
            klass_name = ps[ 'name' ]
            klass = getattr( mod, klass_name )
            self.plugin_classes.append( klass )
            self.plugin_instances.append( klass( self, ps ) )

    def load_plugins_filename_based( self ):
        plugins_dir = os.listdir( self.plugins_path )
        current_dir = os.path.dirname( os.path.abspath( __file__ ) )
        for filename in plugins_dir:
            if filename.endswith('.py'):
                if filename == "__init__.py":
                    continue
                klass_name = os.path.splitext( filename )[ 0 ]
                klass_name = klass_name[ 0 ].upper() + klass_name[ 1: ]
                modulePath =  self.plugins_path + '/' + filename
                cpath = os.path.splitext( modulePath )[ 0 ].replace( os.path.sep, '.' )
                try:
                    mod = importlib.import_module( cpath )
                    self.plugin_modules.append( mod )
                    klass = getattr( mod, klass_name )
                    self.plugin_classes.append( klass )
                    self.plugin_instances.append( klass( self, klass_name ) )
                except ModuleNotFoundError:
                    print('Module not found')
                except AttributeError:
                    print('Method not found')

    def unload_plugins( self ):
        for ins in self.plugin_instances:
            del( ins )
        self.plugin_instances = []

        for cls in self.plugin_classes:
            del( cls )
        self.plugin_classes = []

        for mod in self.plugin_modules:
            del( mod )
        self.plugin_modules = []

    def reload_plugins( self ):
        self.unload_plugins()
        self.load_plugins()

    # bot information

    def self_info( self ):
        return self._self

    def self_id( self ):
        return self.self_info()[ 'id' ]

    def self_name( self ):
        return self.self_info()[ 'name' ]

    def team_info( self ):
        return self._team

    def team_id( self ):
        return self.team_info()[ 'id' ]

    def team_name( self ):
        return self.team_info()[ 'name' ]

    def update_self_info( self, info ):
        self._self = info

    def update_team_info( self, info ):
        self._team = info

    def update_users_list( self, users ):
        for user in users:
            self._users_list[ user[ 'id' ] ] = SlackUser( user )

    def update_channels_list( self, channels ):
        for channel in channels:
            self._channels_list[ channel[ 'id' ] ] = SlackChannel( channel )

    def resolve_channel_id_from_name( self, name ):
        pass

    # plugin commands

    def send_message( self, channel, message, attachments_json = None ):
        self._web_client.chat_postMessage( channel = channel.id, text = message, as_user = False, attachments = attachments_json )

    def send_mention_message( self, channel, user, message, attachments_json = None ):
        mention_message = "<@" + user.id + "> " + message
        self._web_client.chat_postMessage( channel = channel.id, text = mention_message, as_user = False, attachments = attachments_json )

    def send_kick( self, channel, user ):
        self._web_client.channels_kick( channel = channel.id, user = user.id )

    # plugin events

    def on_server_connect( self ):
        for plugin in self.plugin_instances:
            plugin.on_server_connect()

    def process_message( self, data ):
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'user' ] ]
        text = data[ 'text' ]
#        if user.id != self.self_id(): # ignore own message
        for plugin in self.plugin_instances:
            plugin.on_message( channel, user, text )

    def process_message_changed( self, data ):
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'message' ][ 'user' ] ]
        text = data[ 'message' ][ 'text' ]
        prev_user = data[ 'previous_message' ][ 'user' ]
        prev_text = data[ 'previous_message' ][ 'text' ]
#        if user.id != self.self_id(): # ignore own message
        for plugin in self.plugin_instances:
            plugin.on_message_changed( channel, user, text, prev_user, prev_text )

    def on_open( self, **payload ):
        self.update_self_info( payload[ 'data' ][ 'self' ] )
        self.update_team_info( payload[ 'data' ][ 'team' ] )
        self.update_users_list( payload[ 'data' ][ 'users' ] )
        self.update_channels_list( payload[ 'data' ][ 'channels' ] )
        self.load_plugins()
        self.on_server_connect()

    def on_message( self, **payload ):
        data = payload[ 'data' ]
        if 'bot_id' in data:
            return
        if 'subtype' in data:
            if data[ 'subtype' ] == 'message_changed':
                self.process_message_changed( data )
        else:
            self.process_message( data )

    def on_channel_joined( self, **payload ):
        data = payload[ 'data' ]
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'user' ] ]
        for plugin in self.plugin_instances:
            plugin.on_joined( channel, user )

    def on_channel_left( self, **payload ):
        data = payload[ 'data' ]
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'user' ] ]
        for plugin in self.plugin_instances:
            plugin.on_left( channel, user )

    # process slack rtm

    def start( self ):
        self._rtm_client.on( event = 'open', callback = self.on_open )
        self._rtm_client.on( event = 'message', callback = self.on_message )
        self._rtm_client.on( event = 'member_joined_channel', callback = self.on_channel_joined )
        self._rtm_client.on( event = 'member_left_channel', callback = self.on_channel_left )
        self._rtm_client.start()
#        self._rtm_loop.run_until_complete( self._rtm_client.start() )
