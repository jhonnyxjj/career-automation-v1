import { afterEach, expect, test } from "bun:test";
import { apiRequest } from "./api";

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test("reports HTTP failures", async () => {
  globalThis.fetch = () => Promise.resolve(new Response(JSON.stringify({ detail: "Inválido" }), { status: 422 }));
  await expect(apiRequest("/test", {})).rejects.toThrow("Inválido");
});

test("reports network failures", async () => {
  globalThis.fetch = () => Promise.reject(new TypeError("network"));
  await expect(apiRequest("/test", {})).rejects.toThrow("Não foi possível conectar");
});

test("times out a pending request", async () => {
  globalThis.fetch = (_url, init) => new Promise((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
  });
  await expect(apiRequest("/test", {}, 10)).rejects.toThrow("demorou demais");
});
