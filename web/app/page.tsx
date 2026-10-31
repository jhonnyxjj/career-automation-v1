"use client";

import { useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { JobCard } from "@/components/jobs/job-card";
import { ApplicationTracker } from "@/components/jobs/application-tracker";
import { ManualJobImportDialog } from "@/components/jobs/manual-job-import-dialog";
import { CandidateProfileCard } from "@/components/resume/candidate-profile-card";
import { ProfileEditor } from "@/components/resume/profile-editor";
import { ResumeUpload } from "@/components/resume/resume-upload";
import { SearchFilters } from "@/components/search/search-filters";
import { apiRequest, errorMessage } from "@/lib/api";
import type { CandidateProfile, JobListing, JobMatch, SearchFilters as FilterValues } from "@/lib/types";

const seniorityMap: Record<string, string> = { "Estágio": "intern", "Júnior": "junior", "Pleno": "mid", "Sênior": "senior" };
const regionMap: Record<string, string> = { Brasil: "brazil", "Estados Unidos": "united_states", Canadá: "canada", Europa: "europe", "Reino Unido": "united_kingdom", "América Latina": "latin_america", Global: "global" };
const workModeMap: Record<string, string> = { Remoto: "remote", Híbrido: "hybrid", Presencial: "onsite" };

export default function Home() {
  const [profile, setProfile] = useState<CandidateProfile>();
  const [profileConfirmed, setProfileConfirmed] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [needsReview, setNeedsReview] = useState<{ job: JobListing; reason: string }[]>([]);
  const [trackerVersion, setTrackerVersion] = useState(0);
  const [filters, setFilters] = useState<FilterValues>({ seniorities: ["Estágio", "Júnior"], regions: ["Brasil", "Global"], workModes: ["Remoto"], limit: "20" });
  const [sourceReports, setSourceReports] = useState<{ source: string; status: string; count: number; message?: string | null }[]>([]);
  const [status, setStatus] = useState<"idle" | "restoring" | "uploading" | "searching">("restoring");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    apiRequest<CandidateProfile>("/profile/current", { method: "GET" }).then((saved) => {
      if (active) { setProfile(saved); setProfileConfirmed(true); }
    }).catch((error) => {
      if (active && errorMessage(error) !== "Nenhum perfil confirmado.") setError(errorMessage(error));
    }).finally(() => { if (active) setStatus("idle"); });
    return () => { active = false; };
  }, []);

  async function selectResume(file: File) {
    setStatus("uploading"); setError(""); setJobs([]); setNeedsReview([]);
    const form = new FormData(); form.append("file", file);
    try {
      const result = await apiRequest<{ profile: CandidateProfile; warnings?: string[] }>("/profiles/upload", { method: "POST", body: form });
      setProfile(result.profile); setProfileConfirmed(false); setEditingProfile(true); setNotice(result.warnings?.[0] ?? "Perfil identificado.");
    } catch (error) { setError(errorMessage(error)); } finally { setStatus("idle"); }
  }

  async function search(filters: FilterValues) {
    if (!profile) return;
    setStatus("searching"); setError("");
    try {
      const result = await apiRequest<{ jobs: JobListing[]; needs_review: { job: JobListing; reason: string }[]; reports: { source: string; status: string; count: number; message?: string | null }[] }>("/jobs/search", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile_id: profile.id, seniorities: filters.seniorities.map((value) => seniorityMap[value]), regions: filters.regions.map((value) => regionMap[value]), work_modes: filters.workModes.map((value) => workModeMap[value]), limit: Number(filters.limit) }) });
      const skills = new Set(profile.technical_skills.flatMap((group) => group.items));
      setJobs(result.jobs.map((job) => toJobMatch(job, skills)));
      setNeedsReview(result.needs_review);
      setSourceReports(result.reports);
      setTrackerVersion((version) => version + 1);
    } catch (error) { setError(errorMessage(error)); } finally { setStatus("idle"); }
  }

  function addImportedJob(job: JobListing) {
    if (!profile) return;
    const skills = new Set(profile.technical_skills.flatMap((group) => group.items));
    const imported = toJobMatch(job, skills);
    setJobs((current) => [imported, ...current.filter((item) => item.id !== imported.id)]);
    setTrackerVersion((version) => version + 1);
  }

  return <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 lg:py-16"><header className="mb-10 max-w-2xl"><p className="text-sm font-medium text-muted-foreground">Job Matcher</p><h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Encontre vagas compatíveis com seu perfil</h1><p className="mt-3 text-muted-foreground">Envie seu currículo, selecione preferências e veja as vagas mais relevantes.</p></header><div className="grid gap-6 lg:grid-cols-[260px_1fr]"><aside><SearchFilters filters={filters} onChange={setFilters} disabled={!profile || !profileConfirmed || editingProfile || status !== "idle"} loading={status === "searching"} onSearch={search} /></aside><div className="space-y-6">{!profile && status === "idle" && <ResumeUpload onSelect={selectResume} />}{status === "restoring" && <p>Restaurando perfil...</p>}{status === "uploading" && <Card><CardContent className="p-6 text-sm">Identificando perfil...</CardContent></Card>}{notice && <Alert><AlertTitle>Perfil pronto</AlertTitle><AlertDescription>{notice}</AlertDescription></Alert>}{error && <Alert variant="destructive" role="alert"><AlertTitle>Não foi possível concluir</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}{profile && <><CandidateProfileCard profile={profile} />{editingProfile ? <ProfileEditor key={profile.id} profile={profile} onCancel={() => setEditingProfile(false)} onSaved={(saved) => { setProfile(saved); setProfileConfirmed(true); setEditingProfile(false); setNotice("Perfil salvo e confirmado."); }} /> : <div className="flex flex-wrap items-center gap-3"><Button variant="outline" onClick={() => setEditingProfile(true)}>{profileConfirmed ? "Editar perfil" : "Revisar e confirmar perfil"}</Button>{profileConfirmed && <ManualJobImportDialog profileId={profile.id} filters={{ seniorities: filters.seniorities.map((value) => seniorityMap[value]), regions: filters.regions.map((value) => regionMap[value]), work_modes: filters.workModes.map((value) => workModeMap[value]) }} onImported={addImportedJob} />}</div>}<details><summary className="cursor-pointer text-sm">Trocar currículo</summary><ResumeUpload onSelect={selectResume} /></details></>}<Separator /><section aria-labelledby="results-title"><div className="flex items-center justify-between gap-4"><div><h2 id="results-title" className="text-xl font-semibold">Resultados</h2><p className="mt-1 text-sm text-muted-foreground">{status === "searching" ? "Buscando vagas nas fontes configuradas..." : `${jobs.length} vaga(s) encontrada(s).`}</p></div>{jobs.length > 0 && <Badge variant="secondary">{jobs.length}</Badge>}</div>{jobs.length > 0 ? <div className="mt-4 grid gap-4 md:grid-cols-2">{jobs.map((job) => <JobCard key={job.id} job={job} profileId={profile!.id} />)}</div> : <Card className="mt-4 shadow-none"><CardHeader><CardTitle className="text-base">{profile ? profileConfirmed ? "Escolha filtros, busque ou importe uma vaga" : "Confirme o perfil para buscar vagas" : "Envie seu currículo para começar"}</CardTitle></CardHeader><CardContent className="text-sm text-muted-foreground">A busca consulta fontes públicas configuradas. Posts e fontes sem integração podem ser importados manualmente.</CardContent></Card>}</section>{sourceReports.length > 0 && <details className="text-sm"><summary>Relatório das fontes</summary><ul>{sourceReports.map((report) => <li key={report.source}>{report.source}: {report.status} · {report.count} vaga(s){report.message ? ` · ${report.message}` : ""}</li>)}</ul></details>}{needsReview.length > 0 && <section aria-labelledby="review-title"><h2 id="review-title" className="text-xl font-semibold">Vagas para avaliar</h2><p className="mt-1 text-sm text-muted-foreground">Há dados desconhecidos. Confira todos os requisitos antes de considerar estas vagas elegíveis.</p><div className="mt-4 space-y-3">{needsReview.map(({ job, reason }) => <Card key={`${job.source}:${job.external_id ?? job.url}`}><CardContent className="p-4"><p className="font-medium">{job.title} · {job.company}</p><p className="text-sm text-muted-foreground">{reason === "REGION_UNKNOWN" ? "Localização ou elegibilidade geográfica precisa de confirmação" : reason === "WORKPLACE_UNKNOWN" ? "Modalidade desconhecida" : "Área de atuação desconhecida"}</p><a className="text-sm underline" href={job.url} target="_blank" rel="noreferrer">Ver origem</a></CardContent></Card>)}</div></section>}{profile && profileConfirmed && <ApplicationTracker key={profile.id} profileId={profile.id} refreshKey={trackerVersion} />}</div></div></main>;
}

function toJobMatch(job: JobListing, skills: Set<string>): JobMatch {
  const matched = job.technologies.filter((technology) => skills.has(technology));
  return { id: job.external_id ?? job.url, source: job.source, listingType: job.listing_type, title: job.title, company: job.company, location: job.location ?? undefined, workMode: job.workplace_type ?? undefined, technologies: job.technologies, score: job.score, matchedRequirements: matched.length, totalRequirements: job.technologies.length, missingSkills: job.technologies.filter((technology) => !skills.has(technology)), description: job.description ?? undefined, originUrl: job.url, applyUrl: job.apply_url ?? undefined, listing: job };
}
