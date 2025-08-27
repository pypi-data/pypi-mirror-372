# coding: utf-8

from deployv.messaging.basemsg import BaseWorker
from time import sleep
from random import randint
import logging


_logger = logging.getLogger(__name__)


class RabbitWorker(BaseWorker):
    def __init__(self, configuration_object, sender_class, receiver_class,
                 worker_id, worker_manager_class):
        super(RabbitWorker, self).__init__(configuration_object, sender_class, receiver_class,
                                           worker_id)
        self.worker_manager = worker_manager_class

    def run(self):
        """ Worker method, open a channel through a pika connection and
            start consuming
        """
        _logger.debug("Worker %s - waiting for something to do", self._wid)
        self._receiver.run(self.callback)

    def signal_exit(self):
        """ Exit when finished with current loop """
        self._receiver.stop()

    def kill(self):
        """ This kill immediately the process, should not be used """
        self._receiver.stop()
        self.terminate()
        self.join()

    def should_reconnect(self):
        """Method called after a consumer stops, checks if the consumer was
        stopped manually or if it should reconnect.
        """
        if not self._receiver.should_reconnect:
            return False
        self._receiver.stop()
        wait = randint(3, 7)
        _logger.debug('Waiting %s seconds before retry', wait)
        sleep(wait)
        return True

    def callback(self, channel, method, properties, body):
        """ This method is executed as soon as a message arrives, according to the
            `pika documentation
            <http://pika.readthedocs.org/en/latest/examples/blocking_consume.html>`_. The
            parameters are fixed according to it, even if the are unused
        """
        # always ack the messages that don't pass the filters
        res = True
        message = self.check_message(body)
        if message:
            res = self.worker_manager.start_job(self.execute_rpc, message)
        if res:
            channel.basic_ack(method.delivery_tag)
