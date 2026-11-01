"use client";

import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { JobMatch } from "@/lib/types";
import { JobDetails } from "./job-details";
import { TailorResumeDialog } from "../resume-tailoring/tailor-resume-dialog";

const filterReasons: Record<string, string> = {
  REGION_UNKNOWN: "localização ou elegibilidade geográfica não confirmada",
  REGION_NOT_ALLOWED: "localização fora das regiões escolhidas",
  WORKPLACE_UNKNOWN: "modalidade não identificada",
  WORKPLACE_NOT_ALLOWED: "modalidade fora das opções escolhidas",
  ROLE_AREA_UNKNOWN: "área de atuação não identificada",
  ROLE_AREA_NOT_ALLOWED: "área de atuação não selecionada",
  SENIORITY_NOT_ALLOWED: "senioridade fora das opções escolhidas",
  INCOMPATIBLE_STACK: "tecnologias não correspondem ao perfil",
  MID_STACK_NOT_ALLOWED: "vaga plena fora das stacks JavaScript/TypeScript",
  MID_STACK_UNKNOWN: "stack da vaga plena não confirmada",
  NOT_DEVELOPMENT: "cargo não identificado como desenvolvimento",
};

export function JobCard({ job, profileId }: { job: JobMatch; profileId: string }) {
  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="gap-2">
        <div className="flex items-start justify-between gap-4"><div><CardTitle>{job.title}</CardTitle><p className="mt-1 text-sm text-muted-foreground">{job.company}</p></div><Badge variant="secondary">{job.score}%</Badge></div>
        <div className="flex flex-wrap gap-2"><Badge variant="outline">{job.source}</Badge>{job.listingType === "recruiter_post" && <Badge variant="outline">Post de recrutador</Badge>}</div>
        {job.listing.filter_accepted === false && <p className="text-sm text-muted-foreground">Esta vaga importada precisa de avaliação: {filterReasons[job.listing.filter_reason ?? ""] ?? "um filtro não foi atendido"}.</p>}
        <p className="text-sm text-muted-foreground">{[job.location, job.workMode].filter(Boolean).join(" · ")}</p>
      </CardHeader>
      <CardContent className="space-y-4"><div className="flex flex-wrap gap-2">{job.technologies.map((item) => <Badge key={item} variant="outline">{item}</Badge>)}</div><div><p className="text-sm">{job.matchedRequirements} de {job.totalRequirements} requisitos identificados</p><Progress className="mt-2" value={job.totalRequirements ? (job.matchedRequirements / job.totalRequirements) * 100 : 0} /></div>{job.missingSkills.length > 0 && <p className="text-sm text-muted-foreground">Não identificado no currículo: {job.missingSkills.join(", ")}</p>}</CardContent>
      <CardFooter className="mt-auto flex flex-wrap gap-2"><Button asChild variant="outline" size="sm"><a href={job.originUrl} target="_blank" rel="noreferrer"><ExternalLink />Ver origem</a></Button>{job.applyUrl && <Button asChild size="sm"><a href={job.applyUrl} target="_blank" rel="noreferrer"><ExternalLink />Candidatar-se</a></Button>}<JobDetails job={job} /><TailorResumeDialog job={job} profileId={profileId} /><Tooltip><TooltipTrigger asChild><span tabIndex={0}><Button size="sm" variant="ghost">Análise</Button></span></TooltipTrigger><TooltipContent>Mostra requisitos encontrados e ausentes.</TooltipContent></Tooltip></CardFooter>
    </Card>
  );
}
