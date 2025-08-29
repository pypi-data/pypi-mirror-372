import pika
from easter.mailbox import Mailbox


class QueueFactory(object):
    def build(self, channel: pika.channel.Channel, mailbox: Mailbox) -> str:
        queue = mailbox.__class__.__name__

        channel.queue_declare(
            queue=queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        return queue
