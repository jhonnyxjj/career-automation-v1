"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { apiRequest, errorMessage } from "@/lib/api";
import type { JobListing } from "@/lib/types";

type Status = "discovered" | "saved" | "applied" | "interview" | "offer" | "closed";
type Entry = { id: string; job: JobListing; status: Status; notes: string; favorite: boolean; history: { status: Status; at: string }[] };
type Search = { id: string; created_at: string; filters: { regions?: string[]; work_modes?: string[] }; job_ids: string[] };
const statuses: [Status, string][] = [["discovered", "Encontrada"], ["saved", "Salva"], ["applied", "Candidatura enviada manualmente"], ["interview", "Entrevista"], ["offer", "Proposta"], ["closed", "Encerrada"]];

export function ApplicationTracker({ profileId, refreshKey }: { profileId: string; refreshKey: number }) {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [searches, setSearches] = useState<Search[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string>();

  useEffect(() => {
    let active = true;
    apiRequest<{ jobs: Entry[]; searches: Search[] }>(`/tracker/${profileId}`, { method: "GET" }).then((result) => {
      if (active) { setEntries(result.jobs); setSearches(result.searches); setError(""); }
    }).catch((error) => { if (active) setError(errorMessage(error)); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [profileId, refreshKey]);

  function change(id: string, values: Partial<Entry>) {
    setEntries((current) => current.map((entry) => entry.id === id ? { ...entry, ...values } : entry));
  }

  async function save(entry: Entry) {
    setSaving(entry.id); setError("");
    try {
      const saved = await apiRequest<Entry>(`/tracker/${profileId}/jobs/${entry.id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: entry.status, notes: entry.notes, favorite: entry.favorite }) });
      change(entry.id, saved);
    } catch (error) { setError(errorMessage(error)); } finally { setSaving(undefined); }
  }

  return <section aria-labelledby="tracker-title" className="space-y-3"><h2 id="tracker-title" className="text-xl font-semibold">Acompanhamento de vagas</h2>
    <p className="text-sm text-muted-foreground">Registre candidaturas feitas manualmente, notas e favoritos.</p>
    {loading && <p className="text-sm">Carregando acompanhamento...</p>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    {searches.length > 0 && <details className="text-sm"><summary>Histórico de buscas ({searches.length})</summary><ul>{searches.slice().reverse().map((search) => <li key={search.id}>{new Date(search.created_at).toLocaleString("pt-BR")} · {search.job_ids.length} vaga(s) · {(search.filters.regions ?? []).join(", ")}</li>)}</ul></details>}
    {!loading && entries.length === 0 && <p className="text-sm">Busque ou importe vagas para começar.</p>}
    {entries.map((entry) => <article key={entry.id} className="space-y-2 rounded-lg border p-4">
      <p className="font-medium">{entry.job.title} · {entry.job.company}</p>
      <p className="text-sm text-muted-foreground">{entry.job.source} · {entry.job.filter_accepted === false ? "Requer avaliação" : `Compatibilidade ${entry.job.score}%`}</p>
      <a href={entry.job.url} target="_blank" rel="noreferrer" className="text-sm underline">Ver origem</a>
      <label className="block text-sm">Situação<select className="ml-2 rounded-md border bg-background p-1" value={entry.status} onChange={(event) => change(entry.id, { status: event.target.value as Status })}>{statuses.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <label className="block text-sm"><input type="checkbox" checked={entry.favorite} onChange={(event) => change(entry.id, { favorite: event.target.checked })} /> Favorita</label>
      <label className="block text-sm">Observações<textarea className="mt-1 w-full rounded-md border bg-background p-2" value={entry.notes} onChange={(event) => change(entry.id, { notes: event.target.value })} /></label>
      <Button type="button" disabled={!!saving} onClick={() => save(entry)}>{saving === entry.id ? "Salvando..." : "Salvar acompanhamento"}</Button>
      {entry.history.length > 0 && <details className="text-sm"><summary>Histórico de situações</summary><ul>{entry.history.map((event, index) => <li key={index}>{statuses.find(([value]) => value === event.status)?.[1]} · {new Date(event.at).toLocaleString("pt-BR")}</li>)}</ul></details>}
    </article>)}
  </section>;
}
