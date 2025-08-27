# coding: utf-8
import logging
import pika


_logger = logging.getLogger(__name__)


class ReconnectionException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ReconnectionException, self).__init__(message, *args, **kwargs)


class RabbitReceiverV:
    """ This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """
    EXCHANGE_TYPE = 'topic'

    def __init__(self, listener_configuration, worker_id):
        """ Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self.should_reconnect = False
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False

        self._config = listener_configuration
        if self._config.commit_config:
            self._binding_key = '%s.commit' % (self._config.route)
        elif self._config.result_config:
            self._binding_key = self._config.route
        else:
            self._binding_key = '{base}.{wid}'.format(base=self._config.route, wid=worker_id)

    def connect(self):
        """ This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        _logger.debug('Connecting to %s:%s',
                      self._config.parameters.host,
                      self._config.parameters.port)
        return pika.SelectConnection(
                parameters=self._config.parameters,
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error,
                on_close_callback=self.on_connection_closed)

    def close_connection(self):
        """ This method closes the connection to RabbitMQ."""
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            _logger.debug('Connection already closed')
            return
        _logger.debug('Closing connection')
        self._connection.close()

    def on_connection_open(self, unused_connection):
        """ This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        _logger.debug('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        _logger.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, connection, reason):
        """ This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            _logger.debug('Connection closed: %s, reopening', reason)
            self.reconnect()

    def reconnect(self):
        """ Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """ Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        _logger.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """ This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        _logger.debug('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._config.exchange_name)

    def add_on_channel_close_callback(self):
        """ This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        _logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """ Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        _logger.debug('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """ Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        _logger.debug('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(exchange_name,
                                       self.EXCHANGE_TYPE,
                                       callback=self.on_exchange_declareok)

    def on_exchange_declareok(self, unused_frame):
        """ Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        _logger.debug('Exchange declared')
        self.setup_queue(self._binding_key)

    def setup_queue(self, queue_name):
        """ Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        _logger.debug('Declaring queue %s', queue_name)
        self._channel.queue_declare(queue_name, callback=self.on_queue_declareok, durable=True)

    def on_queue_declareok(self, method_frame):
        """ Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        _logger.debug('Binding %s to %s with %s',
                      self._config.exchange_name, self._config.queue_name, self._binding_key)
        self._channel.queue_bind(self._binding_key, self._config.exchange_name,
                                 self._binding_key, callback=self.on_bindok)
        _logger.debug('Binding %s to %s with %s',
                      self._config.exchange_name, self._config.queue_name, self._config.route)
        self._channel.queue_bind(self._config.queue_name, self._config.exchange_name,
                                 self._config.route, callback=self.on_bindok)

    def on_bindok(self, unused_frame):
        """ Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        _logger.debug('Queue bound')
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(prefetch_count=1, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        # TODO: if we need this, remember to set a configurable value
        _logger.debug('QOS set to: 1')
        self.start_consuming()

    def start_consuming(self):
        """ This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming.
        """
        _logger.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self._binding_key, self._callback_funct,
            callback=self.stop_consuming)
        self._consuming = True

    def add_on_cancel_callback(self):
        """ Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        _logger.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """ Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        _logger.info('Consumer was cancelled remotely, shutting down: %r',
                     method_frame)
        if self._channel:
            self._channel.close()

    def stop_consuming(self, *args, **kwargs):
        """ Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            _logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self._consumer_tag, self.on_cancelok)

    def on_cancelok(self, unused_frame):
        """ This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        self._consuming = False
        _logger.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """ Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        _logger.debug('Closing the channel')
        self._channel.close()

    def run(self, callback_funct):
        """ Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._callback_funct = callback_funct
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """ Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        _logger.debug('Stopping')
        if not self._closing:
            self._closing = True
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
        _logger.debug('Stopped')
