from uuid import uuid4

from career.api import JobSearchRequest


def test_search_defaults_to_brazil_and_global_not_europe():
    request = JobSearchRequest(profile_id=str(uuid4()))
    assert request.regions == {'brazil', 'global'}
    assert request.work_modes == {'remote'}
