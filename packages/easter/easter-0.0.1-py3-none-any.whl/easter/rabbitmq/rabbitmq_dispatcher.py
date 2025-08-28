from pika import BlockingConnection
from easter.message import Message
from easter.dispatcher import Dispatcher
from easter.rabbitmq.rabbitmq_connection_factory import RabbitMQConnectionFactory


class RabbitMQDispatcher(Dispatcher):
    def __init__(self, connection_factory: RabbitMQConnectionFactory):
        self.connection_factory = connection_factory

    def dispatch(self, message: Message):
        with self.connection_factory.build() as connection:
            if self.is_exchange_declared(connection, message.message_type):
                self.publish_message(connection, message)

    def publish_message(self, connection: BlockingConnection, message: Message):
        channel = connection.channel()
        serialized_message = message.serialize()

        channel.basic_publish(
            routing_key="#",
            exchange=message.message_type,
            body=serialized_message.encode("utf-8"),
        )

        channel.close()

    def is_exchange_declared(self, connection: BlockingConnection, exchange: str):
        channel = connection.channel()

        try:
            channel.exchange_declare(exchange=exchange, passive=True)
            channel.close()

            return True
        except Exception:
            return False
