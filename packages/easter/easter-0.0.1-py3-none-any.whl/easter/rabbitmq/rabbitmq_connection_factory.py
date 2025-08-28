import pika


class RabbitMQConnectionFactory:
    def __init__(self):
        self.host = "localhost"
        self.port = 5672
        self.username = "guest"
        self.password = "guest"
        self.virtual_host = "/"

    def with_host(self, host):
        self.host = host
        return self

    def with_port(self, port):
        self.port = port
        return self

    def with_credentials(self, username, password):
        self.username = username
        self.password = password
        return self

    def with_virtual_host(self, virtual_host):
        self.virtual_host = virtual_host
        return self

    def build(self):
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=pika.PlainCredentials(
                    username=self.username, password=self.password
                ),
            )
        )
