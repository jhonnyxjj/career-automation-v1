"use client";

import { useState } from "react";
import { LoaderCircle, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import type { SearchFilters as FilterValues } from "@/lib/types";

const seniorities = ["Estágio", "Júnior", "Pleno"];
const regions = ["Brasil", "Estados Unidos", "Canadá", "Europa", "Reino Unido", "América Latina", "Global"];
const workModes = ["Remoto", "Híbrido", "Presencial"];

type SearchFiltersProps = { filters: FilterValues; onChange: (filters: FilterValues) => void; onSearch: (filters: FilterValues) => void; disabled?: boolean; loading?: boolean };

export function SearchFilters({ filters, onChange: setFilters, onSearch, disabled = false, loading = false }: SearchFiltersProps) {
  const [open, setOpen] = useState(false);

  const content = (
    <div className="space-y-6">
      <FilterGroup label="Senioridade" values={seniorities} selected={filters.seniorities} onChange={(seniorities) => setFilters({ ...filters, seniorities })} />
      <Separator />
      <FilterGroup label="Região" values={regions} selected={filters.regions} onChange={(regions) => setFilters({ ...filters, regions })} />
      <Separator />
      <FilterGroup label="Modelo" values={workModes} selected={filters.workModes} onChange={(workModes) => setFilters({ ...filters, workModes })} />
      <Separator />
      <fieldset className="space-y-3">
        <legend className="text-sm font-medium">Quantidade</legend>
        <RadioGroup value={filters.limit} onValueChange={(limit) => setFilters({ ...filters, limit })} className="flex gap-4">
          {["10", "20", "30", "50"].map((limit) => <label key={limit} className="flex items-center gap-2 text-sm"><RadioGroupItem value={limit} />{limit}</label>)}
        </RadioGroup>
      </fieldset>
      <Button className="w-full" disabled={disabled} onClick={() => { onSearch(filters); setOpen(false); }}>{loading ? <><LoaderCircle className="animate-spin" aria-hidden="true" />Buscando vagas...</> : "Buscar vagas"}</Button>
    </div>
  );

  return (
    <>
      <Card className="hidden lg:block"><CardHeader><CardTitle>Filtros</CardTitle></CardHeader><CardContent>{content}</CardContent></Card>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild><Button variant="outline" className="lg:hidden"><SlidersHorizontal />Filtros</Button></SheetTrigger>
        <SheetContent side="left"><SheetHeader><SheetTitle>Filtros</SheetTitle></SheetHeader><div className="mt-6">{content}</div></SheetContent>
      </Sheet>
    </>
  );
}

function FilterGroup({ label, values, selected, onChange }: { label: string; values: string[]; selected: string[]; onChange: (values: string[]) => void }) {
  return <fieldset className="space-y-3"><legend className="text-sm font-medium">{label}</legend>{values.map((value) => <label key={value} className="flex items-center gap-2 text-sm"><Checkbox checked={selected.includes(value)} onCheckedChange={(checked) => onChange(checked ? [...selected, value] : selected.filter((item) => item !== value))} />{value}</label>)}</fieldset>;
}
