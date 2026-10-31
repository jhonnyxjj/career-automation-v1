"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiRequest, errorMessage } from "@/lib/api";
import type { CandidateProfile } from "@/lib/types";

export function ProfileEditor({ profile, onSaved, onCancel }: { profile: CandidateProfile; onSaved: (profile: CandidateProfile) => void; onCancel: () => void }) {
  const [draft, setDraft] = useState(profile);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function save() {
    setSaving(true); setError("");
    try {
      const saved = await apiRequest<CandidateProfile>(`/profile/${profile.id}/confirm`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(draft) });
      onSaved(saved);
    } catch (error) { setError(errorMessage(error)); } finally { setSaving(false); }
  }

  const personalFields = [["name", "Nome"], ["headline", "Título profissional"], ["email", "E-mail"], ["phone", "Telefone"], ["city", "Cidade"], ["state", "Estado"], ["linkedin", "LinkedIn"], ["github", "GitHub"], ["portfolio", "Portfólio"]] as const;
  return <section className="space-y-4 rounded-lg border p-4" aria-labelledby="edit-profile-title">
    <h2 id="edit-profile-title" className="font-semibold">Revise e confirme seu perfil</h2>
    <p className="text-sm text-muted-foreground">Corrija informações extraídas e adicione somente fatos que constam no seu currículo.</p>
    <div className="grid gap-3 sm:grid-cols-2">{personalFields.map(([key, label]) => <label className="text-sm" key={key}>{label}<Input value={draft.personal[key] ?? ""} onChange={(event) => setDraft({ ...draft, personal: { ...draft.personal, [key]: event.target.value } })} /></label>)}</div>
    <label className="block text-sm">Resumo profissional<textarea className="mt-1 min-h-24 w-full rounded-md border bg-background p-2" value={draft.professional_summary ?? ""} onChange={(event) => setDraft({ ...draft, professional_summary: event.target.value })} /></label>
    <label className="block text-sm">Tecnologias (separadas por vírgula)<Input value={draft.technical_skills.flatMap((group) => group.items).join(", ")} onChange={(event) => setDraft({ ...draft, technical_skills: [{ category: "Tecnologias", items: event.target.value.split(",").map((item) => item.trimStart()) }] })} /></label>
    <h3 className="font-medium">Experiências</h3>
    {draft.experiences.map((item, index) => <div className="space-y-2 rounded border p-3" key={index}>
      {([['position', 'Cargo'], ['company', 'Empresa'], ['period', 'Período'], ['location', 'Local']] as const).map(([key, label]) => <label className="block text-sm" key={key}>{label}<Input value={item[key] ?? ""} onChange={(event) => setDraft({ ...draft, experiences: draft.experiences.map((entry, i) => i === index ? { ...entry, [key]: event.target.value } : entry) })} /></label>)}
      <label className="block text-sm">Atividades (uma por linha)<textarea className="w-full rounded-md border bg-background p-2" value={item.bullets.join("\n")} onChange={(event) => setDraft({ ...draft, experiences: draft.experiences.map((entry, i) => i === index ? { ...entry, bullets: event.target.value.split("\n") } : entry) })} /></label>
      <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, experiences: draft.experiences.filter((_, i) => i !== index) })}>Remover experiência</Button>
    </div>)}
    <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, experiences: [...draft.experiences, { company: "", position: "", period: "", bullets: [] }] })}>Adicionar experiência</Button>
    <h3 className="font-medium">Projetos</h3>
    {draft.projects.map((item, index) => <div className="space-y-2 rounded border p-3" key={index}>
      {([['name', 'Nome'], ['context', 'Contexto']] as const).map(([key, label]) => <label className="block text-sm" key={key}>{label}<Input value={item[key] ?? ""} onChange={(event) => setDraft({ ...draft, projects: draft.projects.map((entry, i) => i === index ? { ...entry, [key]: event.target.value } : entry) })} /></label>)}
      <label className="block text-sm">Tecnologias (vírgulas)<Input value={item.technologies.join(", ")} onChange={(event) => setDraft({ ...draft, projects: draft.projects.map((entry, i) => i === index ? { ...entry, technologies: event.target.value.split(",").map((value) => value.trimStart()) } : entry) })} /></label>
      <label className="block text-sm">Atividades (uma por linha)<textarea className="w-full rounded-md border bg-background p-2" value={item.bullets.join("\n")} onChange={(event) => setDraft({ ...draft, projects: draft.projects.map((entry, i) => i === index ? { ...entry, bullets: event.target.value.split("\n") } : entry) })} /></label>
      <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, projects: draft.projects.filter((_, i) => i !== index) })}>Remover projeto</Button>
    </div>)}
    <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, projects: [...draft.projects, { name: "", technologies: [], bullets: [] }] })}>Adicionar projeto</Button>
    <h3 className="font-medium">Formação</h3>
    {draft.education.map((item, index) => <div className="space-y-2 rounded border p-3" key={index}>
      {([['course', 'Curso'], ['institution', 'Instituição'], ['period', 'Período'], ['location', 'Local']] as const).map(([key, label]) => <label className="block text-sm" key={key}>{label}<Input value={item[key] ?? ""} onChange={(event) => setDraft({ ...draft, education: draft.education.map((entry, i) => i === index ? { ...entry, [key]: event.target.value } : entry) })} /></label>)}
      <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, education: draft.education.filter((_, i) => i !== index) })}>Remover formação</Button>
    </div>)}
    <Button type="button" variant="outline" onClick={() => setDraft({ ...draft, education: [...draft.education, { institution: "", course: "", period: "" }] })}>Adicionar formação</Button>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <div className="flex gap-2"><Button disabled={saving || !draft.personal.name.trim()} onClick={save}>{saving ? "Salvando..." : "Salvar e confirmar"}</Button><Button variant="outline" disabled={saving} onClick={onCancel}>Cancelar</Button></div>
  </section>;
}
