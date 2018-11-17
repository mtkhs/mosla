import json
import time
import threading
import requests
from datetime import datetime
from slacklib import SlackPlugin

class DocomoNaturalChatting( SlackPlugin ):

    def bot_construct( self ):
        self.api_key = self.setting[ 'api_key' ]
        self.app_id = ''
        self.app_recv_time = ''
        self.regist()

    def regist( self ):
        req_url = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration?APIKEY=' + self.api_key
        req_body = {
            'botId': 'Chatting',
            'appKind': 'Slack',
        }
        req_headers = { 'Content-type': 'application/json; charset=UTF-8' }

        r = requests.post( req_url, data = json.dumps( req_body ), headers = req_headers )
        data = r.json()
        self.app_id = data[ 'appId' ]

    def on_message( self, user, channel, message ):
        if self.is_mention_to_me( message ):
            to_user, message = self.parse_mention_text( message )
            reply = self.get_reply( message )
            self.send_mention_message( channel, user, reply )

    def create_timestamp( self ):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_reply( self, text ):
        req_url = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY=' + self.api_key
        req_body = {
            'language': 'ja-JP',
            'botId': 'Chatting',
            'appId': self.app_id,
            'voiceText': '',
            'appRecvTime': '',
            'appSendTime': ''
        }
        req_headers = { 'Content-type': 'application/json; charset=UTF-8' }

        req_body[ 'voiceText' ] = text
        send_time = self.create_timestamp()
        req_body[ 'appSendTime' ] = send_time
        req_body[ 'appRecvTime' ] = self.app_recv_time

        r = requests.post( req_url, data = json.dumps( req_body ), headers = req_headers )
        self.app_recv_time = self.create_timestamp()

        resp = r.json()
        resp_message = resp[ 'systemText' ][ 'expression' ]

        return resp_message

