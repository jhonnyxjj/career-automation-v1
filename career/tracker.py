from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from .models import JobListing, SearchResult
from .normalizer import canonical_url, job_fingerprint
from .profile_store import _atomic_write


TRACKER_DIR = Path(".data") / "tracker"
_lock = RLock()


def _read(profile_id: str) -> dict:
    path = TRACKER_DIR / f"{profile_id}.json"
    if not path.exists():
        return {"version": 1, "jobs": [], "searches": []}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("version") != 1 or not isinstance(state.get("jobs"), list) or not isinstance(state.get("searches"), list):
        raise ValueError("Dados de acompanhamento inválidos.")
    return state


def _write(profile_id: str, state: dict) -> None:
    _atomic_write(TRACKER_DIR / f"{profile_id}.json", json.dumps(state, ensure_ascii=False, indent=2))


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _upsert(state: dict, job: JobListing, *, update_existing: bool = True) -> dict:
    for entry in state["jobs"]:
        existing = JobListing.model_validate(entry["job"])
        same_id = job.external_id and existing.external_id == job.external_id and existing.source == job.source
        if same_id or canonical_url(existing.url) == canonical_url(job.url) or job_fingerprint(existing) == job_fingerprint(job):
            if update_existing:
                entry["job"] = job.model_dump(mode="json")
                entry["updated_at"] = _now()
            return entry
    entry = {"id": str(uuid4()), "job": job.model_dump(mode="json"), "favorite": False, "status": "discovered", "notes": "", "created_at": _now(), "updated_at": _now(), "history": []}
    state["jobs"].append(entry)
    return entry


def load_tracker(profile_id: str) -> dict:
    with _lock:
        return _read(profile_id)


def save_job(profile_id: str, job: JobListing) -> dict:
    with _lock:
        state = _read(profile_id)
        entry = _upsert(state, job)
        _write(profile_id, state)
        return entry


def save_search(profile_id: str, filters: dict, result: SearchResult) -> None:
    with _lock:
        state = _read(profile_id)
        ids = [_upsert(state, job)["id"] for job in result.jobs]
        for review in getattr(result, "needs_review", []):
            job = review.job.model_copy(update={"filter_accepted": False, "filter_reason": review.reason})
            _upsert(state, job, update_existing=False)
        state["searches"].append({"id": str(uuid4()), "created_at": _now(), "filters": filters, "job_ids": ids, "reports": [report.model_dump(mode="json") for report in result.reports]})
        _write(profile_id, state)


def update_job(profile_id: str, job_id: str, *, status: str, notes: str, favorite: bool) -> dict:
    with _lock:
        state = _read(profile_id)
        entry = next((entry for entry in state["jobs"] if entry["id"] == job_id), None)
        if entry is None:
            raise FileNotFoundError("Vaga não encontrada.")
        if entry["status"] != status:
            entry["history"].append({"status": status, "at": _now()})
        if (entry["status"], entry["notes"], entry["favorite"]) != (status, notes, favorite):
            entry.update(status=status, notes=notes, favorite=favorite, updated_at=_now())
            _write(profile_id, state)
        return entry
