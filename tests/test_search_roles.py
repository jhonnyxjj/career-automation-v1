from uuid import uuid4

from career.api import search_profile
from career.filters import hard_filter
from career.models import CandidateProfile, JobListing, ResumePersonalDetails


def test_search_profile_excludes_frontend_only_roles():
    candidate = CandidateProfile(id=str(uuid4()), personal=ResumePersonalDetails(name='Pessoa'))
    profile = search_profile(candidate, {'junior'}, {'brazil'}, {'remote'})
    job = JobListing(source='Teste', title='Frontend Developer Junior', company='Empresa',
                     url='https://example.com/job', location='Brasil', workplace_type='remote', seniority='junior')
    assert hard_filter(job, profile).reason == 'ROLE_AREA_NOT_ALLOWED'
