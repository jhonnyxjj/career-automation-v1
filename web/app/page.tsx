"use client";

import { useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { JobCard } from "@/components/jobs/job-card";
import { CandidateProfileCard } from "@/components/resume/candidate-profile-card";
import { ResumeUpload } from "@/components/resume/resume-upload";
import { SearchFilters } from "@/components/search/search-filters";
import { apiPath, readError } from "@/lib/api";
import type { CandidateProfile, JobListing, JobMatch, SearchFilters as FilterValues } from "@/lib/types";

const seniorityMap: Record<string, string> = { "Estágio": "intern", "Júnior": "junior", "Pleno": "mid", "Sênior": "senior" };
const regionMap: Record<string, string> = { Brasil: "brazil", "Estados Unidos": "united_states", Canadá: "canada", Europa: "europe", "Reino Unido": "united_kingdom", "América Latina": "latin_america", Global: "global" };
const workModeMap: Record<string, string> = { Remoto: "remote", Híbrido: "hybrid", Presencial: "onsite" };

export default function Home() {
  const [profile, setProfile] = useState<CandidateProfile>();
  const [profileConfirmed, setProfileConfirmed] = useState(false);
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [status, setStatus] = useState<"idle" | "uploading" | "searching">("idle");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function selectResume(file: File) {
    setStatus("uploading"); setError(""); setJobs([]);
    const form = new FormData(); form.append("file", file);
    const response = await fetch(apiPath("/profiles/upload"), { method: "POST", body: form });
    if (!response.ok) { setError(await readError(response)); setStatus("idle"); return; }
    const result = await response.json();
    setProfile(result.profile); setProfileConfirmed(false); setNotice(result.warnings?.[0] ?? "Perfil identificado."); setStatus("idle");
  }

  async function search(filters: FilterValues) {
    if (!profile) return;
    setStatus("searching"); setError("");
    const response = await fetch(apiPath("/jobs/search"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile_id: profile.id, seniorities: filters.seniorities.map((value) => seniorityMap[value]), regions: filters.regions.map((value) => regionMap[value]), work_modes: filters.workModes.map((value) => workModeMap[value]), limit: Number(filters.limit) }) });
    if (!response.ok) { setError(await readError(response)); setStatus("idle"); return; }
    const result = await response.json();
    const skills = new Set(profile.technical_skills.flatMap((group) => group.items));
    setJobs(result.jobs.map((job: JobListing) => toJobMatch(job, skills)));
    setStatus("idle");
  }

  return <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 lg:py-16"><header className="mb-10 max-w-2xl"><p className="text-sm font-medium text-muted-foreground">Job Matcher</p><h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Encontre vagas compatíveis com seu perfil</h1><p className="mt-3 text-muted-foreground">Envie seu currículo, selecione preferências e veja as vagas mais relevantes.</p></header><div className="grid gap-6 lg:grid-cols-[260px_1fr]"><aside><SearchFilters disabled={!profile || !profileConfirmed || status !== "idle"} onSearch={search} /></aside><div className="space-y-6">{!profile && <ResumeUpload onSelect={selectResume} />}{status === "uploading" && <Card><CardContent className="p-6 text-sm">Identificando perfil...</CardContent></Card>}{notice && <Alert><AlertTitle>Perfil pronto</AlertTitle><AlertDescription>{notice}</AlertDescription></Alert>}{error && <Alert variant="destructive" role="alert"><AlertTitle>Não foi possível concluir</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}{profile && <><CandidateProfileCard profile={profile} /><label className="flex items-center gap-2 text-sm"><Checkbox id="profile-confirmed" checked={profileConfirmed} onCheckedChange={(checked) => setProfileConfirmed(checked === true)} />Revisei o perfil identificado e confirmo que ele representa meu currículo.</label></>}<Separator /><section aria-labelledby="results-title"><div className="flex items-center justify-between gap-4"><div><h2 id="results-title" className="text-xl font-semibold">Resultados</h2><p className="mt-1 text-sm text-muted-foreground">{status === "searching" ? "Buscando vagas nas fontes configuradas..." : `${jobs.length} vaga(s) encontrada(s).`}</p></div>{jobs.length > 0 && <Badge variant="secondary">{jobs.length}</Badge>}</div>{jobs.length > 0 ? <div className="mt-4 grid gap-4 md:grid-cols-2">{jobs.map((job) => <JobCard key={job.id} job={job} profileId={profile!.id} />)}</div> : <Card className="mt-4 shadow-none"><CardHeader><CardTitle className="text-base">{profile ? profileConfirmed ? "Escolha filtros e busque vagas" : "Confirme o perfil para buscar vagas" : "Envie seu currículo para começar"}</CardTitle></CardHeader><CardContent className="text-sm text-muted-foreground">A busca consulta apenas as fontes configuradas e informa falhas por fonte.</CardContent></Card>}</section></div></div></main>;
}

function toJobMatch(job: JobListing, skills: Set<string>): JobMatch {
  const matched = job.technologies.filter((technology) => skills.has(technology));
  return { id: job.external_id ?? job.url, title: job.title, company: job.company, location: job.location ?? undefined, workMode: job.workplace_type ?? undefined, technologies: job.technologies, score: job.score, matchedRequirements: matched.length, totalRequirements: job.technologies.length, missingSkills: job.technologies.filter((technology) => !skills.has(technology)), description: job.description ?? undefined, sourceUrl: job.apply_url ?? job.url, listing: job };
}
