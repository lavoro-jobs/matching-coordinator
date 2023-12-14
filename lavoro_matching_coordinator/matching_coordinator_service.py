import os

import jsonpickle

from lavoro_library.amqp import RabbitMQConsumer, RabbitMQProducer
from lavoro_library.database import Database
from lavoro_library.model.message_schemas import ItemToMatch


class MatchingCoordinatorService:
    def __init__(self):
        self.db = Database(os.environ["DB_CONNECTION_STRING"])
        self.item_to_match_consumer = RabbitMQConsumer(os.environ["AMQP_URL"], "item_to_match")
        self.match_to_calculate_producer = RabbitMQProducer(os.environ["AMQP_URL"], "match_to_calculate")

    def start(self):
        self.item_to_match_consumer.consume(self._message_inflow_callback)

    @staticmethod
    def _message_inflow_callback(channel, method, properties, body):
        message: ItemToMatch = jsonpickle.decode(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    service = MatchingCoordinatorService()
    service.start()
