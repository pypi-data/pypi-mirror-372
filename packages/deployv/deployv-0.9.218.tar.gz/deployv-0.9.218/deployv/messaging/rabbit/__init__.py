# coding: utf-8

from .worker import RabbitWorker
from .rabbitv import FileRabbitConfiguration, BaseRabbitConfiguration
from .receiverv import RabbitReceiverV
from .senderv import RabbitSenderV
import logging

logging.getLogger("pika").setLevel(logging.WARNING)


CONFIG_CLASSES = {
    'base': BaseRabbitConfiguration,
    'file': FileRabbitConfiguration
}


def factory(config_object, worker_id, worker_manager):
    logging.getLogger("pika").propagate = config_object.config.deployer.get('pika_logs')
    rabbit_worker = RabbitWorker(config_object,
                                 RabbitSenderV,
                                 RabbitReceiverV,
                                 worker_id,
                                 worker_manager_class=worker_manager
                                 )
    return rabbit_worker
