import os

import jsonpickle

from lavoro_library.amqp import RabbitMQConsumer, RabbitMQProducer
from lavoro_library.model.message_schemas import ApplicantProfileToMatch, ItemToMatch, JobPostToMatch, MatchToCalculate
from lavoro_matching_coordinator.database import queries


class MatchingCoordinatorService:
    def __init__(self):
        self.item_to_match_consumer = RabbitMQConsumer(os.environ["AMQP_URL"], "item_to_match")
        self.match_to_calculate_producer = RabbitMQProducer(os.environ["AMQP_URL"], "match_to_calculate")

    def start(self):
        self.item_to_match_consumer.consume(self._message_inflow_callback)

    def _message_inflow_callback(self, channel, method, properties, body):
        message: ItemToMatch = ItemToMatch(**jsonpickle.decode(body))
        self._process_item_to_match(message)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _process_item_to_match(self, item_to_match: ItemToMatch):
        matches_to_calculate = self._create_matches_to_calculate(item_to_match)
        for match_to_calculate in matches_to_calculate:
            self.match_to_calculate_producer.publish(match_to_calculate)
        self._save_item_to_match(item_to_match)

    def _create_matches_to_calculate(self, item_to_match: ItemToMatch):
        if isinstance(item_to_match.data, JobPostToMatch):
            job_post_to_match = item_to_match.data
            applicant_profiles_to_match = queries.get_items_to_match("applicant_profile")
            for applicant_profile_to_match in applicant_profiles_to_match:
                yield self._generate_match_to_calculate(job_post_to_match, applicant_profile_to_match)
        else:
            applicant_profile_to_match = item_to_match.data
            job_posts_to_match = queries.get_items_to_match("job_post")
            for job_post_to_match in job_posts_to_match:
                yield self._generate_match_to_calculate(job_post_to_match, applicant_profile_to_match)

    def _generate_match_to_calculate(
        self, job_post_to_match: JobPostToMatch, applicant_profile_to_match: ApplicantProfileToMatch
    ):
        return MatchToCalculate(
            job_post_to_match=job_post_to_match, applicant_profile_to_match=applicant_profile_to_match
        )

    def _save_item_to_match(self, item_to_match: ItemToMatch):
        return queries.create_or_update_item_to_match(item_to_match)


if __name__ == "__main__":
    service = MatchingCoordinatorService()
    service.start()
