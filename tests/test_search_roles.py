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


def test_explicit_frontend_title_is_not_overridden_by_backend_mention():
    candidate = CandidateProfile(id=str(uuid4()), personal=ResumePersonalDetails(name='Pessoa'))
    profile = search_profile(candidate, {'junior'}, {'brazil'}, {'remote'})
    job = JobListing(source='Teste', title='Frontend Developer Junior', company='Empresa',
                     url='https://example.com/job', location='Brasil', workplace_type='remote', seniority='junior',
                     description='Desenvolvimento de interfaces e colaboração com a equipe backend.')
    assert hard_filter(job, profile).reason == 'ROLE_AREA_NOT_ALLOWED'


def test_generic_software_title_can_use_description_to_identify_backend():
    candidate = CandidateProfile(id=str(uuid4()), personal=ResumePersonalDetails(name='Pessoa'))
    profile = search_profile(candidate, {'junior'}, {'brazil'}, {'remote'})
    job = JobListing(source='Teste', title='Software Developer Junior', company='Empresa',
                     url='https://example.com/job', location='Brasil', workplace_type='remote', seniority='junior',
                     description='Desenvolvimento de APIs backend.')
    assert hard_filter(job, profile).accepted


def test_title_explicitly_including_backend_remains_eligible():
    candidate = CandidateProfile(id=str(uuid4()), personal=ResumePersonalDetails(name='Pessoa'))
    profile = search_profile(candidate, {'junior'}, {'brazil'}, {'remote'})
    job = JobListing(source='Teste', title='Frontend and Backend Developer Junior', company='Empresa',
                     url='https://example.com/job', location='Brasil', workplace_type='remote', seniority='junior')
    assert hard_filter(job, profile).accepted
