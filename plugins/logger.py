import os
import re
from slacklib import SlackPlugin
from datetime import datetime

class Logger( SlackPlugin ):

    def bot_construct( self ):
        self.log_dir = self.setting[ 'log_dir' ]
        if not os.path.exists( self.log_dir ):
            os.mkdir( self.log_dir )

    def create_channel_filename( self, channel ):
        return "_#" + channel.name + "-" + datetime.now().strftime( "%Y%m%d" ) + ".log"

    def create_im_filename( self, channel ):
        return "_" + channel.user + "-" + datetime.now().strftime( "%Y%m%d" ) + ".log"

    def create_timestamp( self ):
        return datetime.now().strftime( "%Y/%m/%d %H:%M:%S" )

    def create_channel_line( self, channel, user, message ):
        timestamp = self.create_timestamp()
        line = timestamp + " #" + channel.name + " " + user.name + " > " + self.normalize_text( message )
        return line

    def create_im_line( self, channel, user, message ):
        timestamp = self.create_timestamp()
        line = timestamp + " " + channel.user + " " + user.name + " > " + self.normalize_text( message )
        return line

    def normalize_date( self, text ):
        return text

    def normalize_special_command( self, text ):
        mention_pattern = re.compile( r'<!(channel|here|everyone)>' )
        for match in mention_pattern.finditer( text ):
            text = text.replace( match.group( 0 ), "@" + match.group( 1 ) )
        return text

    def normalize_user_group( self, text ):
        return text

    def normalize_user( self, text ):
        mention_pattern = re.compile( r'<@([UW][0-9A-Z]{8})>' )
        for match in mention_pattern.finditer( text ):
            user = self.bot._users_list[ match.group( 1 ) ]
            text = text.replace( match.group( 0 ), "@" + user.name )
        return text

    def normalize_channel( self, text ):
        mention_pattern = re.compile( r'<#(C[0-9A-Z]{8})\|([^>]+)>' )
        for match in mention_pattern.finditer( text ):
            text = text.replace( match.group( 0 ), "#" + match.group( 2 ) )
        return text

    def normalize_url( self, text ):
        mention_pattern = re.compile( r'<(https?://[^>]+)>' )
        for match in mention_pattern.finditer( text ):
            if match.group( 1 ).rfind( '|' ) < 0:
                str = match.group( 1 )
            else:
                full_url, short_url = match.group( 1 ).rsplit( '|', 1 )
                str = short_url
            text = text.replace( match.group( 0 ), str )
        return text

    def normalize_text( self, text ):
        text = self.normalize_user( text )
        text = self.normalize_channel( text )
        text = self.normalize_special_command( text )
        text = self.normalize_url( text )
        text = text.replace( '&amp;', '&' ).replace( '&lt;', '<' ).replace( '&gt;', '>' )
        return text

    def put_log( self, log_filename, text ):
        with open( self.log_dir + "/" + log_filename, "a", encoding="utf-8" ) as log_file:
            log_file.write( text + "\n" )

    def download_attachment_file( self ):
        pass

    def on_message( self, channel, user, message ):
        if channel.is_channel():
            line = self.create_channel_line( channel, user, message )
            filename = self.create_channel_filename( channel )
            self.put_log( filename, line )
        elif channel.is_group():
            pass
        elif channel.is_im():
            line = self.create_im_line( channel, user, message )
            filename = self.create_im_filename( channel )
            self.put_log( filename, line )
