from easter.rabbitmq import RabbitMQConnectionFactory
from easter.rabbitmq import RabbitMQDispatcher
from easter.rabbitmq import RabbitMQConsumer

from tests.user import User
from tests.user_created_mailbox import UserCreatedMailbox
from tests.user_created_message import UserCreatedMessage
from tests.user_deleted_message import UserDeletedMessage

connection_factory = (
    RabbitMQConnectionFactory()
    .with_host("localhost")
    .with_port(5672)
    .with_credentials("rabbit", "32132111")
)


def test_rabbitmq():
    user = User("test_user", "test@example.com")
    user_created_message = UserCreatedMessage(user)
    user_deleted_message = UserDeletedMessage(user)
    user_created_mailbox = UserCreatedMailbox()

    dispatcher = RabbitMQDispatcher(connection_factory)

    with RabbitMQConsumer(connection_factory, [user_created_mailbox]) as consumer:
        dispatcher.dispatch(user_created_message)
        dispatcher.dispatch(user_deleted_message)

    message = user_created_mailbox.last_message

    assert message.user.name == user.name
    assert message.user.email == user.email
    assert user_created_mailbox.received_messages == 1
    assert type(message) in user_created_mailbox.supported_message_types
    assert type(message) is UserCreatedMessage
