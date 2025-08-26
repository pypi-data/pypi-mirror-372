import logging


class EventHandler:
    def handle(self, event):
        try:
            handler_name = event.get('name', '')
            method = getattr(self, handler_name, None)
            if callable(method):
                method(event)
            else:
                self.catch_all(event)
        except Exception as e:
            logging.error('Error handling event: {}'.format(e))

    def catch_all(self, event):
        logging.info('Unhandled <{}> event: {}'.format(self.__class__.__name__, event))
