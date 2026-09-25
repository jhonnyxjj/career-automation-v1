"use client";

import { ChangeEvent, useRef } from "react";
import { FileUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type ResumeUploadProps = {
  onSelect: (file: File) => void;
};

export function ResumeUpload({ onSelect }: ResumeUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file?.type === "application/pdf") onSelect(file);
  }

  return (
    <Card className="border-dashed shadow-none">
      <CardContent className="flex min-h-64 flex-col items-center justify-center gap-4 p-8 text-center">
        <FileUp className="size-7 text-muted-foreground" aria-hidden="true" />
        <div>
          <p className="font-medium">Arraste seu currículo aqui</p>
          <p className="mt-1 text-sm text-muted-foreground">Apenas arquivos PDF.</p>
        </div>
        <Input ref={inputRef} type="file" accept="application/pdf" className="sr-only" onChange={selectFile} />
        <Button type="button" variant="secondary" onClick={() => inputRef.current?.click()}>
          Selecionar arquivo
        </Button>
      </CardContent>
    </Card>
  );
}
