import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import type { JobMatch } from "@/lib/types";

export function JobDetails({ job }: { job: JobMatch }) {
  return <Dialog><DialogTrigger asChild><Button size="sm" variant="outline">Detalhes</Button></DialogTrigger><DialogContent className="max-h-[85vh] overflow-y-auto"><DialogHeader><DialogTitle>{job.title}</DialogTitle></DialogHeader><p>{job.company} · {[job.location, job.workMode].filter(Boolean).join(" · ")}</p><Separator /><section><h3 className="font-medium">Match geral: {job.score}%</h3><p className="mt-1 text-sm text-muted-foreground">{job.matchedRequirements} de {job.totalRequirements} requisitos identificados.</p></section><section><h3 className="font-medium">Skills encontradas</h3><div className="mt-2 flex flex-wrap gap-2">{job.technologies.map((skill) => <Badge key={skill}>{skill}</Badge>)}</div></section>{job.missingSkills.length > 0 && <section><h3 className="font-medium">Skills não identificadas</h3><p className="mt-1 text-sm text-muted-foreground">{job.missingSkills.join(", ")}</p></section>}{job.description && <section><h3 className="font-medium">Descrição</h3><p className="mt-1 whitespace-pre-line text-sm text-muted-foreground">{job.description}</p></section>}{job.requirements && <section><h3 className="font-medium">Requisitos</h3><ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted-foreground">{job.requirements.map((item) => <li key={item}>{item}</li>)}</ul></section>}</DialogContent></Dialog>;
}
