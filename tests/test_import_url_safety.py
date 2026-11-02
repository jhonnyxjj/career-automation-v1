from uuid import uuid4

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from career.api import ManualJobImportRequest, app


@pytest.mark.parametrize('url', [
    'http://localhost/job', 'http://sub.localhost/job', 'http://host.local/job',
    'http://127.0.0.1/job', 'http://127.1/job', 'http://0x7f000001/job',
    'http://0177.0.0.1/job', 'http://%31%32%37.0.0.1/job', 'http://localhost./job',
    'http://10.1.2.3/job', 'http://169.254.169.254/job', 'http://[::1]/job',
    'http://[::ffff:127.0.0.1]/job',
])
@pytest.mark.parametrize('field', ['source_url', 'apply_url'])
def test_manual_import_rejects_local_or_private_destinations(url, field):
    values = {'profile_id': str(uuid4()), 'source': 'LinkedIn', 'title': 'Backend',
              'company': 'Empresa', 'description': 'Vaga fictícia', 'source_url': 'https://example.com/job'}
    values[field] = url
    with pytest.raises(ValidationError):
        ManualJobImportRequest(**values)


def test_manual_import_accepts_public_links():
    request = ManualJobImportRequest(profile_id=str(uuid4()), source='LinkedIn', title='Backend',
                                     company='Empresa', description='Vaga fictícia',
                                     source_url='https://example.com/job', apply_url='https://jobs.example.org/apply')
    assert request.apply_url == 'https://jobs.example.org/apply'


def test_manual_import_accepts_public_literal_ip():
    request = ManualJobImportRequest(profile_id=str(uuid4()), source='Teste', title='Backend',
                                     company='Empresa', description='Vaga fictícia', source_url='https://8.8.8.8/job')
    assert request.source_url == 'https://8.8.8.8/job'


def test_api_rejects_private_import_url_before_loading_profile():
    response = TestClient(app).post('/jobs/import', json={
        'profile_id': str(uuid4()), 'source': 'Teste', 'title': 'Backend', 'company': 'Empresa',
        'description': 'Vaga fictícia', 'source_url': 'http://127.0.0.1/job',
    })
    assert response.status_code == 422
