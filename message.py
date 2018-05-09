# coding=utf-8
import logging
from random import choice

import main
import messages
from bot import Bot


class Message(dict):
    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.handlers = {
            'text': self.handle_text,
            'contact': self.handle_contact,
            'new_chat_participant': self.handle_new_chat_participant,
            'left_chat_participant': self.left_chat_participant,
        }

    def get_sender(self):
        return self['chat']

    def get_sender_id(self):
        return self.get_sender()['id']

    def get_id(self):
        return self['message_id']

    def handle(self):
        for handler_type, handler in self.handlers.items():
            if handler_type in self:
                return handler()
        return {}

    def _response(self, method, is_reply=False, **kwargs):
        _response = {
            'method': method,
            'chat_id': self.get_sender_id(),
        }
        if is_reply:
            _response['reply_to_message_id'] = self.get_id()
        if kwargs:
            _response.update(kwargs)
        return _response

    def response(self, text, is_reply=False):
        return self._response("sendMessage", is_reply, disable_web_page_preview=True, text=text)

    def gps_response(self, gps):
        return self._response("sendLocation", True, latitude=gps[0], longitude=gps[1])

    def get_session(self):
        sender_id = self.get_sender_id()
        if sender_id not in main.SESSIONS:
            main.SESSIONS[sender_id] = Bot(self.get_sender())

        return main.SESSIONS[sender_id]

    def handle_text(self):
        logging.debug(self['text'])
        session = self.get_session()
        text = self['text']
        if text.startswith('/'):
            handler = session.handle_command
        else:
            handler = session.handle_text
        try:
            output = handler(text)
        except Exception:  # pragma: no cover
            return {}

        if isinstance(output, tuple):
            return self.gps_response(output)
        elif output:
            return self.response(output, is_reply=True)

    def handle_contact(self):
        return self.response("id = %s" % self['contact'].get('user_id', "none"), is_reply=True)

    def handle_new_chat_participant(self):
        output = messages.BOT_GREETING_TEMPL % self['new_chat_participant'].get('first_name')
        output += choice(messages.BOT_GREETING_PHRASES)
        return self.response(output)

    def left_chat_participant(self):
        return self.response(messages.BOT_LEFT_PARTICIPANT)
