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

    def response(self, text, is_reply=False):
        _response = {
            'method': "sendMessage",
            'chat_id': self.get_sender_id(),
            'text': text,
            'disable_web_page_preview': True,
        }
        if is_reply:
            _response['reply_to_message_id'] = self.get_id()
        return _response

    def handle_text(self):
        logging.debug(self['text'])
        sender_id = self.get_sender_id()
        if sender_id not in main.SESSIONS:
            main.SESSIONS[sender_id] = Bot(self.get_sender())

        session = main.SESSIONS[sender_id]
        text = self['text']
        try:
            if text[0] == '/':
                output = session.handle_command(text)
            else:
                output = session.handle_text(text)
        except Exception:  # pragma: no cover
            return {}

        if isinstance(output, tuple):
            return {'method': "sendLocation",
                    'chat_id': sender_id,
                    'reply_to_message_id': self.get_id(),
                    'latitude': output[0],
                    'longitude': output[1]}
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
