# coding: utf-8

import logging
from deployv.messaging.basemsg import BasicMessage
from deployv.messaging.rabbit import rabbitv, senderv
from pika.exceptions import ConnectionClosed
from datetime import datetime

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SenderMessage:

    def __init__(self, config):
        self.__config = config
        rabbit_obj = rabbitv.FileRabbitConfiguration(self.__config, 'result')
        self._rabbit_sender = senderv.RabbitSenderV(
            rabbit_obj, self.__config.deployer.get('node_id'))

    def _create_message(self, body, res_model=False, res_id=False):
        """The Create a BasicMessage object to send it to Orchest, also
        it set the message body and identify if the it belong a message to
        `notification.mixin` model or it use the model configure in
        the `DeployvConfig` object.

        :param body: The body that will set to the message.
        :type: dict
        :return: The message that will sent to Orchest.
        :rtype: BasicMessage object.
        """
        values = {
            'sender_node_id': self.__config.sender_node_id or self.__config.deployer.get(
                'node_id'),
            'receiver_node_id': self.__config.receiver_node_id or self.__config.deployer.get(
                'orchest_receiver_id'),
            'user_id': self.__config.user_id,
            'response_to': self.__config.response_to,
            'res_model': res_model or self.__config.res_model,
            'res_id': self.__config.res_id if not res_model else res_id,
        }
        message = BasicMessage(values)
        body.update({
            'task_id': self.__config.instance_config.get('task_id'),
            'customer_id': self.__config.instance_config.get('customer_id'),
        })
        message.set_message_body(body, message_type='result')
        return message

    def _send_message(self, message):
        """The method try send the message to Rabbit server.

        :param message: The message that will send to Rabbit.
        :type message: BasicMessage object.
        """
        if not message.receiver_node_id:
            logger.debug('Failed to send the message: The receiver is required')
            return
        try:
            self._rabbit_sender.send_message(message)
        except ConnectionClosed:
            logger.warning('Failed to send the message: Lost connection with rabbit')

    def send_result(self, body=False, log=False, log_type='INFO', metrics=False):
        """Method fo send a message via rabbit to the specified topic in anywhere of process.

        :param body: The data than will send.
        :type: dict
        :param log: The log post and sent.
        :type: str
        :param log_type: the log type of message logged.
        :type: str
        """
        body = body or {}
        if log:
            self._update_body(body, self._create_log_msg(log, log_type))
        if metrics:
            self._update_body(body, self._create_metric_msg(**metrics))
        message = self._create_message(body)
        self._send_message(message)

    def _update_body(self, body, res):
        """If the `body` is empty, `res` will replace the value of `body` else
        it save the value of `res` in the `command` key.

        :param body: The body of message than will send to `Orchest`.
        :type: dict
        :param res: Extra data than will send to `Orchest`.
        :type: dict
        """
        if not body:
            body.update(res)
        else:
            body.update({res.get('command'): res})

    def _create_log_msg(self, msg, log_type='INFO'):
        """Method to create `save_log` message that will send to `Orchest`.

        :param msg: the log post and sent.
        :type msg: str
        :param log_type: the log type of message logged.
        :type: str
        """
        ins_cfg = self.__config.instance_config
        getattr(logger, log_type.lower())(msg)
        values = {'time': datetime.utcnow().isoformat(' '), 'type': log_type, 'msg': msg,
                  'task': ins_cfg.get('task_id'), 'customer': ins_cfg.get('customer_id')}
        return {
            'command': 'save_log',
            'log': '%(time)s %(type)s deployv.%(task)s.%(customer)s: %(msg)s' % values,
        }

    def _create_metric_msg(self, statuses, stage):
        """Method to create `metric` message that will send to `Orchest`.

        :param statuses: The statuses of metrics.
        :type: list.
        :param stage: The stage of statuses.
        :type: str.
        """
        date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        metrics = []
        for status in statuses:
            metric = {'stage': stage, 'status': status, 'date': date}
            metrics.append(metric)
        return {'command': 'metric', 'metrics': metrics}
