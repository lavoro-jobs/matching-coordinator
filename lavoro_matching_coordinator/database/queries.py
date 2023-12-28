from datetime import datetime
import jsonpickle
from lavoro_library.model.message_schemas import ApplicantProfileToMatch, ItemToMatch, JobPostToMatch
from lavoro_matching_coordinator.database import db


def create_or_update_item_to_match(item_to_match: ItemToMatch):
    query = """
        INSERT INTO items_to_match (id, item_type, item_to_match)
        VALUES (%s, %s, %s)
        ON CONFLICT (id, item_type) DO UPDATE
        SET item_to_match = EXCLUDED.item_to_match
    """

    item_type = "applicant_profile" if isinstance(item_to_match.data, ApplicantProfileToMatch) else "job_post"
    item_id = (
        item_to_match.data.applicant_account_id if item_type == "applicant_profile" else item_to_match.data.job_post_id
    )

    query_tuple = (query, (item_id, item_type, jsonpickle.encode(item_to_match.data.model_dump())))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_items_to_match(item_type: str):
    query_tuple = (
        """
        SELECT item_to_match
        FROM items_to_match
        WHERE item_type = %s
    """,
        (item_type,),
    )

    result = db.execute_one(query_tuple)
    if result["result"]:
        for item in result["result"]:
            decoded_data = jsonpickle.decode(item["item_to_match"])
            if item_type == "applicant_profile":
                yield ApplicantProfileToMatch(**decoded_data)
            else:
                job_post_to_match = JobPostToMatch(**decoded_data)
                if job_post_to_match.end_date > datetime.now():
                    yield JobPostToMatch(**decoded_data)
    else:
        return []


def delete_item_to_match(item_type: str, item_id: str):
    query_tuple = (
        """
        DELETE FROM items_to_match
        WHERE item_type = %s AND id = %s
    """,
        (item_type, item_id),
    )

    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1
