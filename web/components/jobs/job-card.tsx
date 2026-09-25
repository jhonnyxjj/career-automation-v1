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

export function JobCard({ job, profileId }: { job: JobMatch; profileId: string }) {
  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="gap-2">
        <div className="flex items-start justify-between gap-4"><div><CardTitle>{job.title}</CardTitle><p className="mt-1 text-sm text-muted-foreground">{job.company}</p></div><Badge variant="secondary">{job.score}%</Badge></div>
        <p className="text-sm text-muted-foreground">{[job.location, job.workMode].filter(Boolean).join(" · ")}</p>
      </CardHeader>
      <CardContent className="space-y-4"><div className="flex flex-wrap gap-2">{job.technologies.map((item) => <Badge key={item} variant="outline">{item}</Badge>)}</div><div><p className="text-sm">{job.matchedRequirements} de {job.totalRequirements} requisitos identificados</p><Progress className="mt-2" value={(job.matchedRequirements / job.totalRequirements) * 100} /></div>{job.missingSkills.length > 0 && <p className="text-sm text-muted-foreground">Não identificado no currículo: {job.missingSkills.join(", ")}</p>}</CardContent>
      <CardFooter className="mt-auto flex flex-wrap gap-2"><Button asChild variant="outline" size="sm"><a href={job.sourceUrl} target="_blank" rel="noreferrer"><ExternalLink />Ver vaga</a></Button><JobDetails job={job} /><TailorResumeDialog job={job} profileId={profileId} /><Tooltip><TooltipTrigger asChild><span tabIndex={0}><Button size="sm" variant="ghost">Análise</Button></span></TooltipTrigger><TooltipContent>Mostra requisitos encontrados e ausentes.</TooltipContent></Tooltip></CardFooter>
    </Card>
  );
}
