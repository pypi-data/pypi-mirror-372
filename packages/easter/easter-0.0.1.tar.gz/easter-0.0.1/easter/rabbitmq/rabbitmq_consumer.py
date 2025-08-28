import threading
from typing import List
from easter.mailbox import Mailbox
from easter.message import Message
from easter.consumer import Consumer
from easter.rabbitmq.factories.queue_collection_factory import QueueCollectionFactory
from easter.rabbitmq.rabbitmq_connection_factory import RabbitMQConnectionFactory


class RabbitMQConsumer(Consumer):
    def __init__(
        self, connection_factory: RabbitMQConnectionFactory, mailboxes: List[Mailbox]
    ):
        self.connection_factory = connection_factory
        self.mailboxes = mailboxes
        self.consumer_thread = None
        self.connection = None
        self.channel = None

    def consume(self):
        queue_factory = QueueCollectionFactory()
        self.connection = self.connection_factory.build()
        self.channel = self.connection.channel()

        for queue, mailbox in queue_factory.build(self.channel, self.mailboxes):
            message_handler = self.get_message_handler(mailbox)
            self.channel.basic_consume(queue=queue, on_message_callback=message_handler)

        self.consumer_thread = threading.Thread(target=self.start_consuming)
        self.consumer_thread.start()

    def close(self):
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
            self.channel.close()

        if self.connection and self.connection.is_open:
            self.connection.close()

        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join()

    def start_consuming(self):
        try:
            if self.channel is not None:
                self.channel.start_consuming()
        except:
            pass

    def get_message_handler(self, mailbox):
        def message_handler(channel, method, properties, body):
            serialized_message = body.decode("utf-8")
            message = Message.deserialize(serialized_message)

            if type(message) in mailbox.supported_message_types:
                mailbox.handle(message)

            channel.basic_ack(delivery_tag=method.delivery_tag)

        return message_handler
