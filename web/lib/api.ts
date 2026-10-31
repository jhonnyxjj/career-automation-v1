const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function apiPath(path: string) {
  return `${apiUrl}${path}`;
}

export async function readError(response: Response) {
  const body = await response.json().catch(() => null);
  return typeof body?.detail === "string" ? body.detail : "Não foi possível concluir a solicitação.";
}

export async function apiRequest<T>(path: string, init: RequestInit, timeoutMs = 60000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(apiPath(path), { ...init, signal: controller.signal });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(typeof body?.detail === "string" ? body.detail : "Não foi possível concluir a solicitação.");
    }
    return await response.json() as T;
  } catch (error) {
    if (controller.signal.aborted) throw new Error("A solicitação demorou demais. Tente novamente.");
    if (error instanceof TypeError) throw new Error("Não foi possível conectar ao serviço. Verifique a conexão e tente novamente.");
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Não foi possível concluir a solicitação.";
}
