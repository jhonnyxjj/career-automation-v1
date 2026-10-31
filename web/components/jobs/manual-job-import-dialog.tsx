"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { apiRequest, errorMessage } from "@/lib/api";
import type { JobListing, ManualJobImport } from "@/lib/types";

const sources = ["LinkedIn", "Indeed", "Gupy", "Vagas.com.br", "ProgramaThor", "InfoJobs", "Sólides Vagas", "Glassdoor", "Meu Padrinho", "Outro"];

const emptyJob: ManualJobImport = {
  source: "LinkedIn",
  listing_type: "recruiter_post",
  title: "",
  company: "",
  description: "",
  source_url: "",
};

export function ManualJobImportDialog({ profileId, filters, onImported }: { profileId: string; filters: { seniorities: string[]; regions: string[]; work_modes: string[] }; onImported: (job: JobListing) => void }) {
  const [open, setOpen] = useState(false);
  const [job, setJob] = useState<ManualJobImport>(emptyJob);
  const [status, setStatus] = useState<"idle" | "loading">("idle");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading"); setError("");
    try {
      const result = await apiRequest<JobListing>("/jobs/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...job, ...filters, profile_id: profileId, apply_url: job.apply_url || undefined, location: job.location || undefined }),
      });
      onImported(result);
      setJob(emptyJob); setOpen(false);
    } catch (error) { setError(errorMessage(error)); } finally { setStatus("idle"); }
  }

  return <Dialog open={open} onOpenChange={setOpen}><DialogTrigger asChild><Button variant="outline">Importar vaga ou post</Button></DialogTrigger><DialogContent className="max-h-[85vh] overflow-y-auto"><DialogHeader><DialogTitle>Importar vaga ou post de recrutador</DialogTitle></DialogHeader><form className="space-y-4" onSubmit={submit}><p className="text-sm text-muted-foreground">Cole o conteúdo que você visualizou. A candidatura continua sendo feita manualmente no link informado.</p><label className="block text-sm font-medium">Fonte<select className="mt-1 w-full rounded-md border bg-background px-3 py-2" value={job.source} onChange={(event) => setJob({ ...job, source: event.target.value })}>{sources.map((source) => <option key={source}>{source}</option>)}</select></label><label className="block text-sm font-medium">Tipo<select className="mt-1 w-full rounded-md border bg-background px-3 py-2" value={job.listing_type} onChange={(event) => setJob({ ...job, listing_type: event.target.value as ManualJobImport["listing_type"] })}><option value="recruiter_post">Post de recrutador</option><option value="job">Vaga</option></select></label><label className="block text-sm font-medium">Cargo<Input className="mt-1" value={job.title} onChange={(event) => setJob({ ...job, title: event.target.value })} required /></label><label className="block text-sm font-medium">Empresa<Input className="mt-1" value={job.company} onChange={(event) => setJob({ ...job, company: event.target.value })} required /></label><label className="block text-sm font-medium">Descrição da vaga<textarea className="mt-1 min-h-36 w-full rounded-md border bg-background px-3 py-2 text-sm" value={job.description} onChange={(event) => setJob({ ...job, description: event.target.value })} required /></label><label className="block text-sm font-medium">URL da origem<Input className="mt-1" type="url" value={job.source_url} onChange={(event) => setJob({ ...job, source_url: event.target.value })} required /></label><label className="block text-sm font-medium">URL para candidatura (opcional)<Input className="mt-1" type="url" value={job.apply_url ?? ""} onChange={(event) => setJob({ ...job, apply_url: event.target.value })} /></label><label className="block text-sm font-medium">Localização (opcional)<Input className="mt-1" value={job.location ?? ""} onChange={(event) => setJob({ ...job, location: event.target.value })} /></label>{error && <p className="text-sm text-destructive" role="alert">{error}</p>}<Button className="w-full" disabled={status === "loading"} type="submit">{status === "loading" ? "Importando..." : "Analisar vaga"}</Button></form></DialogContent></Dialog>;
}
