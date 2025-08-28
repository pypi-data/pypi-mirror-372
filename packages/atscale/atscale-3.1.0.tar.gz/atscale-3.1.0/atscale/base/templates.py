import logging
from typing import Dict

logger = logging.getLogger(__name__)


def create_query_for_post_request(
    query: str,
    catalog_name: str,
    use_aggs=True,
    gen_aggs=False,
    fake_results=False,
    use_local_cache=True,
    use_aggregate_cache=True,
    timeout=10,
) -> Dict:
    return {
        "language": "SQL",
        "query": query,
        "context": {
            "environment": {"id": "default"},
            "project": {"name": catalog_name},
        },
        "aggregation": {"useAggregates": use_aggs, "genAggregates": gen_aggs},
        "fakeResults": fake_results,
        "dryRun": False,  # keeping this here, so we check if it works in the future, see AL-512, such a low num ik
        "useLocalCache": use_local_cache,
        "useAggregateCache": use_aggregate_cache,
        "timeout": f"{timeout}.minutes",
    }
