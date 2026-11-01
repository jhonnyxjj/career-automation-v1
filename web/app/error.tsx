"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ErrorPage({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error("Erro inesperado ao renderizar a aplicação.");
  }, []);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-4 py-10 sm:px-6">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Não foi possível carregar esta página</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Ocorreu um erro inesperado. Tente carregar a página novamente.
          </p>
          {process.env.NODE_ENV === "development" && (
            <p className="break-words rounded-md bg-muted p-3 font-mono text-xs">
              {error.message}
            </p>
          )}
          <Button onClick={retry}>Tentar novamente</Button>
        </CardContent>
      </Card>
    </main>
  );
}
