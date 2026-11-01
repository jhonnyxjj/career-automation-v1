import { expect, test } from "@playwright/test";
import path from "node:path";

test("profile, import, application and tailored resume survive a refresh", async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await page.locator('input[type="file"]').first().setInputFiles(path.join(__dirname, "resume-fixture.pdf"));
  await expect(page.getByRole("heading", { name: "Revise e confirme seu perfil" })).toBeVisible();
  await page.getByLabel("Nome", { exact: true }).fill("Pessoa Teste E2E");
  await page.getByLabel("Tecnologias (separadas por vírgula)").fill("TypeScript, Node.js");
  await page.getByRole("button", { name: "Salvar e confirmar" }).click();
  await expect(page.getByText("Perfil salvo e confirmado.")).toBeVisible();
  await page.reload();
  await expect(page.getByText("Pessoa Teste E2E")).toBeVisible();

  await page.getByRole("button", { name: "Importar vaga ou post" }).click();
  await page.getByLabel("Cargo").fill("Backend Developer Junior");
  await page.getByLabel("Empresa").fill("Empresa Fictícia E2E");
  await page.getByLabel("Descrição da vaga").fill("Backend junior remoto no Brasil com TypeScript e Node.js");
  await page.getByLabel("URL da origem").fill(`https://example.com/e2e/${Date.now()}`);
  await page.getByLabel("Localização (opcional)").fill("Brasil");
  await page.getByRole("button", { name: "Analisar vaga" }).click();
  const tracker = page.getByRole("region", { name: "Acompanhamento de vagas" });
  await expect(tracker.getByText("Empresa Fictícia E2E", { exact: false })).toBeVisible();
  await tracker.getByLabel("Situação").selectOption("applied");
  await tracker.getByLabel("Favorita").check();
  await tracker.getByLabel("Observações").fill("Nota fictícia E2E");
  await tracker.getByRole("button", { name: "Salvar acompanhamento" }).click();
  await expect(tracker.getByText("Histórico de situações")).toBeVisible();
  await page.reload();
  await expect(tracker.getByLabel("Situação")).toHaveValue("applied");
  await expect(tracker.getByLabel("Favorita")).toBeChecked();
  await expect(tracker.getByLabel("Observações")).toHaveValue("Nota fictícia E2E");
  await tracker.getByRole("button", { name: "Ver vaga e adaptar currículo" }).click();
  await page.getByRole("button", { name: "Adaptar currículo", exact: true }).click();
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByText("Currículo adaptado com sucesso.")).toBeVisible();
  const pdfResponse = await page.request.get(await page.getByRole("link", { name: "Baixar PDF" }).getAttribute("href") as string);
  expect((await pdfResponse.body()).subarray(0, 5).toString()).toBe("%PDF-");
  const texResponse = await page.request.get(await page.getByRole("link", { name: "Baixar .tex" }).getAttribute("href") as string);
  expect(await texResponse.text()).toContain("Pessoa Teste E2E");
  await page.getByRole("button", { name: "Close" }).click();
  await page.route("**/jobs/search", (route) => route.abort());
  await page.getByRole("button", { name: "Buscar vagas" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Não foi possível" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Buscar vagas" })).toBeEnabled();
});

test("invalid PDF reports an error without hanging", async ({ page }) => {
  await page.goto("/");
  const invalid = { name: "invalid.pdf", mimeType: "application/pdf", buffer: Buffer.from("not a PDF") };
  const replacement = page.getByText("Trocar currículo");
  if (await replacement.isVisible()) await replacement.click();
  await page.locator('input[type="file"]').first().setInputFiles(invalid);
  await expect(page.getByRole("alert").filter({ hasText: "PDF válido" })).toBeVisible();
  await expect(page.getByText("Identificando perfil...")).toHaveCount(0);
});
