const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function apiPath(path: string) {
  return `${apiUrl}${path}`;
}

export async function readError(response: Response) {
  const body = await response.json().catch(() => null);
  return body?.detail ?? "Não foi possível concluir a solicitação.";
}
