import pika
from easter.mailbox import Mailbox


class QueueExchangeFactory(object):
    def build(self, channel: pika.channel.Channel, queue_name: str, exchange_name: str):
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type="direct",
            durable=True,
            auto_delete=False,
        )
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key="#",
        )
