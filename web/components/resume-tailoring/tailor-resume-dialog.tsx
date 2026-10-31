"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { apiPath, apiRequest, errorMessage } from "@/lib/api";
import type { GeneratedResume, JobMatch } from "@/lib/types";

export function TailorResumeDialog({ job, profileId }: { job: JobMatch; profileId: string }) {
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [generated, setGenerated] = useState<GeneratedResume>();
  const [error, setError] = useState("");

  async function start() {
    setStatus("loading");
    try {
      setGenerated(await apiRequest<GeneratedResume>("/resumes/tailor", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile_id: profileId, job: job.listing }) }));
      setStatus("done");
    } catch (error) { setError(errorMessage(error)); setStatus("error"); }
  }

  return <Dialog onOpenChange={(open) => !open && setStatus("idle")}><DialogTrigger asChild><Button size="sm">Adaptar currículo</Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>Adaptar currículo para {job.company}</DialogTitle></DialogHeader>{status === "idle" && <Button onClick={start}>Gerar currículo adaptado</Button>}{status === "loading" && <div className="space-y-3" aria-live="polite"><p className="text-sm">Adaptando currículo...</p><Progress value={66} /><Skeleton className="h-8 w-full" /></div>}{status === "error" && <div className="space-y-3" role="alert"><p className="text-sm text-destructive">{error}</p><Button onClick={start}>Tentar novamente</Button></div>}{status === "done" && generated && <div className="space-y-4" aria-live="polite"><p className="text-sm">Currículo adaptado com sucesso.</p><div className="flex flex-wrap gap-2"><Button asChild variant="outline"><a href={apiPath(`/resumes/${generated.id}/download/tex`)}>Baixar .tex</a></Button>{generated.pdf_available && <Button asChild><a href={apiPath(`/resumes/${generated.id}/download/pdf`)}>Baixar PDF</a></Button>}</div>{!generated.pdf_available && <p className="text-xs text-muted-foreground">PDF indisponível: o serviço não possui pdflatex configurado.</p>}</div>}</DialogContent></Dialog>;
}
