import os
import importlib
import time
import slack_sdk
import asyncio
from slacklib import SlackUser
from slacklib import SlackPlugin
from slacklib import SlackChannel
from slacklib import SlackGroup
from slacklib import SlackIM
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.errors import SlackApiError

class SlackBot():

    def __init__( self, setting ):
        xoxb_token = setting[ 'slack' ][ 'xoxb_token' ]
        xapp_token = setting[ 'slack' ][ 'xapp_token' ]
        self._web_client = WebClient( token = xoxb_token )
        self._sm_client = SocketModeClient( app_token = xapp_token, web_client = self._web_client )
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
#        current_dir = os.path.dirname( os.path.abspath( __file__ ) )
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

    def self_user( self ):
        return self._self

    def self_id( self ):
        u = self.self_user()
        return u.id

    def self_name( self ):
        return self.self_user().name

    def team_info( self ):
        return self._team

    def team_id( self ):
        return self.team_info()[ 'id' ]

    def team_name( self ):
        return self.team_info()[ 'name' ]

    def update_self_user( self, user ):
        self._self = user

    def update_team_info( self, info ):
        self._team = info

    def update_users_list( self, users ):
        for user in users:
            self._users_list[ user[ 'id' ] ] = SlackUser( user )

    def update_groups_list( self, groups ):
        for group in groups:
            self._channels_list[ group[ 'id' ] ] = SlackGroup( group )

    def update_ims_list( self, ims ):
        for im in ims:
            self._channels_list[ im[ 'id' ] ] = SlackIM( im )

    def update_channels_list( self, channels ):
        for channel in channels:
            self._channels_list[ channel[ 'id' ] ] = SlackChannel( channel )

    def resolve_channel_id_from_name( self, name ):
        pass

    # plugin commands

    def send_message( self, channel, message, attachments_json = None ):
        self._web_client.chat_postMessage( channel = channel.id, text = message, attachments = attachments_json )

    def send_mention_message( self, channel, user, message, attachments_json = None ):
        mention_message = "<@" + user.id + "> " + message
        self._web_client.chat_postMessage( channel = channel.id, text = mention_message,  attachments = attachments_json )


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

    def on_message( self, payload ):
        data = payload
        if 'bot_id' in data:
            return
        if 'subtype' in data:
            if data[ 'subtype' ] == 'message_changed':
                self.process_message_changed( data )
        else:
            self.process_message( data )

    def on_channel_joined( self, **payload ):
        data = payload
        channel = data[ 'channel' ]
        self._channels_list[ channel[ 'id' ] ] = SlackChannel( channel )

    def on_channel_left( self, **payload ):
        data = payload
        del self._channels_list[ data[ 'channel' ] ]
        # TODO: It should be not delete the channel and It must be update the status such as a 'is_member'.
        # self._channels_list[ data[ 'channel' ] ].is_member = False

    def on_member_joined_channel( self, **payload ):
        data = payload
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'user' ] ]
        for plugin in self.plugin_instances:
            plugin.on_joined( channel, user )

    def on_member_left_channel( self, **payload ):
        data = payload
        channel = self._channels_list[ data[ 'channel' ] ]
        user = self._users_list[ data[ 'user' ] ]
        for plugin in self.plugin_instances:
            plugin.on_left( channel, user )

    # process slack rtm

    def on_socket_mode_request( self, client: SocketModeClient, req: SocketModeRequest ):
        if req.type == "events_api":
            # Acknowledge the request anyway
            response = SocketModeResponse( envelope_id = req.envelope_id )
            client.send_socket_mode_response( response )

            if req.payload[ 'event' ][ 'type' ] == 'open':
                self.on_open( req.payload[ 'event' ] )
            elif req.payload[ 'event' ][ 'type' ] == 'message':
                self.on_message( req.payload[ 'event' ] )
            elif req.payload[ 'event' ][ 'type' ] == 'channel_joined':
                self.on_channel_joined( req.payload[ 'event' ] )
            elif req.payload[ 'event' ][ 'type' ] == 'channel_left':
                self.on_channel_left( req.payload[ 'event' ] )
            elif req.payload[ 'event' ][ 'type' ] == 'member_joined_channel':
                self.on_member_joined_channel( req.payload[ 'event' ] )
            elif req.payload[ 'event' ][ 'type' ] == 'member_left_channel':
                self.on_member_left_channel( req.payload[ 'event' ] )

    def start( self ):
        self._sm_client.socket_mode_request_listeners.append( self.on_socket_mode_request )
        self._sm_client.connect()

        response = self._web_client.users_list()
        self.update_users_list( response[ 'members' ] )

        response = self._web_client.conversations_list()
        self.update_channels_list( response[ 'channels' ] )

        response = self._web_client.team_info()
        self.update_team_info( response[ 'team' ] )

        response = self._web_client.auth_test()
        self_id = response[ 'user_id' ]
        self.update_self_user( self._users_list[ self_id ] )

        self.load_plugins()
        self.on_server_connect()

        from threading import Event
        Event().wait()

