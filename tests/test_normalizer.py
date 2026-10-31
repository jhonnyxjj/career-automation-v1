from career.models import RawJob
from career.normalizer import normalize_job, normalized_text


def test_normalizes_text_url_seniority_workplace_and_technologies():
    job = normalize_job(
        RawJob(
            source="  Lever ",
            external_id="42",
            title="  Desenvolvedor   JavaScript Jr. ",
            company=" Empresa  X ",
            description="Remote role with Node.js, PostgreSQL and Docker.",
            location=" Brasil ",
            url="https://example.com/jobs/42/?utm_source=test&b=2",
        )
    )

    assert job.title == "Desenvolvedor JavaScript Jr."
    assert job.company == "Empresa X"
    assert job.url == "https://example.com/jobs/42?b=2"
    assert job.seniority == "junior"
    assert job.workplace_type == "remote"
    assert {"JavaScript", "Node.js", "PostgreSQL", "Docker"}.issubset(job.technologies)
    assert "Java" not in job.technologies


def test_normalized_text_removes_accents_and_extra_space():
    assert normalized_text("  Híbrido — São Paulo ") == "hibrido — sao paulo"


def test_infers_in_office_as_onsite():
    job = normalize_job(RawJob(source="Greenhouse", title="Backend Engineer", company="Acme", url="https://example.com/1", location="In-Office"))
    assert job.workplace_type == "onsite"


def test_hybrid_takes_precedence_over_remote_mentions():
    job = normalize_job(RawJob(source="Example", title="Backend Engineer", company="Acme", url="https://example.com/1", workplace_type="remote", description="Hybrid position with remote days"))
    assert job.workplace_type == "hybrid"
