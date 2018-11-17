import json
import time
import websocket
from xml.etree import ElementTree
import threading
from slacklib import SlackPlugin
from slacklib import SlackChannel

class Earthquake( SlackPlugin ):

    EVENT_ID_FILENAME = 'kishou_last_event_id'

    def bot_construct( self ):
        self.channel = self.bot.channels_list[ self.setting[ 'channel_id' ] ]
        self.ws = None
        self.sleep_count = 0
        self.last_event_id = self.restore_last_event_id()

    def store_last_event_id( self, id ):
        self.last_event_id = id
        fp = open( self.EVENT_ID_FILENAME, 'w' )
        fp.write( id )
        fp.close()

    def restore_last_event_id( self ):
        result = None

        try:
            fp = open( self.EVENT_ID_FILENAME, 'r' )
            result = fp.read()
            fp.close()
        except FileNotFoundError:
            result = "0"

        return result

    def parse_title( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Head'
                        '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Title' )
        return ele.text

    def parse_event_id( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Head'
                        '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}EventID' )
        return ele.text

    def parse_description( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Head'
                        '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Headline'
                        '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Text' )
        return ele.text

    def parse_earthquake_area_name( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Body'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Earthquake'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Hypocenter'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Area'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Name' )
        return ele.text

    def parse_earthquake_locations( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Body'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Earthquake'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Hypocenter'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Area'
                        '/{http://xml.kishou.go.jp/jmaxml1/elementBasis1/}Coordinate' )
        return ele.get( "description" )

    def parse_earthquake_magnitude( self, root ):
        ele = root.find( '{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Body'
                        '/{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}Earthquake'
                        '/{http://xml.kishou.go.jp/jmaxml1/elementBasis1/}Magnitude' )
        return ele.get( "description" )

    def parse_info_list( self, root ):
        eles = root.findall( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Head'
                            '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Headline'
                            '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Information' )

        return eles

    def parse_info_item_list( self, info ):
        items = info.findall( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Item' )
        return items

    def parse_item_kind_name( self, item ):
        ele = item.find( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Kind'
                        '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Name' )
        return ele.text

    def parse_item_area_name( self, item ):
        ele = item.find( '{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Areas'
                            '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Area'
                            '/{http://xml.kishou.go.jp/jmaxml1/informationBasis1/}Name' )
        return ele.text

    def parse_item_detail( self, item ):
        detail = self.parse_item_kind_name( item ) + " " + self.parse_item_area_name( item )
        return detail

    def create_earthquake_attachment( self, title, description, area_name, locations, magnitude ):
        attachments_json = [
            {
                "attachment_type": "default",
                "fallback": "Earthquake information",
                "text": title + "\n" + description + "\n" + area_name + "\n" + locations + "\n" + magnitude
            }
        ]

        return attachments_json

    def on_ws_message( self, message ):
        elem = ElementTree.fromstring( message )

        # check the message is new or not
        event_id = self.parse_event_id( elem )
        if( int( event_id ) <= int( self.last_event_id ) ):
            return

        # store latest event_id
        self.store_last_event_id( event_id )

        title = self.parse_title( elem )
        description = self.parse_description( elem )
        area_name = self.parse_earthquake_area_name( elem )
        locations = self.parse_earthquake_locations( elem )
        magnitude = self.parse_earthquake_magnitude( elem )

        info_list = self.parse_info_list( elem )
        if( info_list != [] ):
            for info in info_list:
                print( info.get( 'type' ) )
                items = self.parse_info_item_list( info )
                for item in items:
                    detail = self.parse_item_detail( item )
                    print( detail )

        attachments_json = self.create_earthquake_attachment( title, description, area_name, locations, magnitude )
        self.bot.send_message( self.channel, "", attachments_json = json.dumps( attachments_json ) )

    def on_ws_error( self, error ):
        print( error )

    def on_ws_close( self ):
        pass

    def on_ws_open( self ):
        self.ws.send( "filter 地震情報" )
        self.ws.send( "start" )

    def start( self ):
        self.ws = websocket.WebSocketApp( url = "ws://cloud1.aitc.jp:443/websocket/WSServlet",
                                    on_message = self.on_ws_message,
                                    on_error = self.on_ws_error,
                                    on_close = self.on_ws_close,
                                    on_open = self.on_ws_open
        )
        self.ws.run_forever( ping_interval = 50 )

    def stop( self ):
        self.ws.close()

    def on_server_connect( self ):
        t = threading.Thread( target = self.start, daemon = True )
        t.start()
