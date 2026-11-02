import { expect, test } from "@playwright/test";
import path from "node:path";

test("profile, import, application and tailored resume survive a refresh", async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await page.locator('input[type="file"]').first().setInputFiles(path.join(__dirname, "resume-fixture.pdf"));
  await expect(page.getByRole("heading", { name: "Revise e confirme seu perfil" })).toBeVisible();
  await page.getByLabel("Nome", { exact: true }).fill("Pessoa Teste E2E");
  await page.getByLabel("Tecnologias (separadas por vírgula)").fill("TypeScript, Node.js");
  await page.getByRole("button", { name: "Adicionar experiência" }).click();
  const experience = page.getByRole("button", { name: "Remover experiência" }).locator("..");
  await experience.getByLabel("Cargo").fill("Desenvolvedora");
  await experience.getByLabel("Empresa").fill("Empresa Confirmada");
  await experience.getByLabel("Período").fill("2021-2024");
  await experience.getByLabel("Atividades (uma por linha)").fill("Criou APIs em TypeScript");
  await page.getByRole("button", { name: "Adicionar projeto" }).click();
  const project = page.getByRole("button", { name: "Remover projeto" }).locator("..");
  await project.getByLabel("Nome").fill("Projeto Confirmado");
  await page.getByRole("button", { name: "Adicionar formação" }).click();
  const education = page.getByRole("button", { name: "Remover formação" }).locator("..");
  await education.getByLabel("Curso").fill("Computação");
  await education.getByLabel("Instituição").fill("Universidade Confirmada");
  await education.getByLabel("Período").fill("2017-2021");
  await page.getByRole("button", { name: "Salvar e confirmar" }).click();
  await expect(page.getByText("Perfil salvo e confirmado.")).toBeVisible();
  await page.reload();
  await expect(page.getByText("Pessoa Teste E2E")).toBeVisible();
  await page.getByRole("button", { name: "Editar perfil" }).click();
  await expect(page.getByLabel("Empresa", { exact: true })).toHaveValue("Empresa Confirmada");
  await expect(page.getByLabel("Instituição")).toHaveValue("Universidade Confirmada");
  await expect(page.getByRole("button", { name: "Remover projeto" }).locator("..").getByLabel("Nome")).toHaveValue("Projeto Confirmado");
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();

  await page.getByRole("button", { name: "Importar vaga ou post" }).click();
  await page.getByLabel("Cargo").fill("Backend Developer Junior");
  await page.getByLabel("Empresa").fill("Empresa Fictícia E2E");
  await page.getByLabel("Descrição da vaga").fill("Backend junior remoto no Brasil com TypeScript e Node.js. Requer 2 anos de experiência.");
  await page.getByLabel("URL da origem").fill(`https://example.com/e2e/${Date.now()}`);
  await page.getByLabel("Localização (opcional)").fill("Brasil");
  await page.getByRole("button", { name: "Analisar vaga" }).click();
  await page.getByRole("button", { name: "Detalhes", exact: true }).click();
  await expect(page.getByText("Menção de 2–3 anos de experiência: -5 pontos")).toBeVisible();
  await page.getByRole("button", { name: "Close" }).click();
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
  const texUrl = await page.getByRole("link", { name: "Baixar .tex" }).getAttribute("href") as string;
  const texResponse = await page.request.get(texUrl);
  const tex = await texResponse.text();
  for (const fact of ["Pessoa Teste E2E", "Empresa Confirmada", "Projeto Confirmado", "Universidade Confirmada"]) expect(tex).toContain(fact);
  await page.getByRole("button", { name: "Close" }).click();
  await page.route("**/resumes/tailor", (route) => route.request().method() === "OPTIONS"
    ? route.continue()
    : route.fulfill({ headers: { "access-control-allow-origin": "http://localhost:13000" }, json: { id: texUrl.split("/").at(-3), pdf_available: false } }));
  await page.getByRole("button", { name: "Adaptar currículo", exact: true }).click();
  await page.getByRole("button", { name: "Gerar currículo adaptado" }).click();
  await expect(page.getByText("PDF indisponível. O arquivo .tex está disponível para download.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Baixar .tex" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Baixar PDF" })).toHaveCount(0);
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

test("search shows uncertain location and partial source failure", async ({ page }) => {
  await page.goto("/");
  const replacement = page.getByText("Trocar currículo");
  if (await replacement.isVisible()) await replacement.click();
  await page.locator('input[type="file"]').first().setInputFiles(path.join(__dirname, "resume-fixture.pdf"));
  await page.getByRole("button", { name: "Salvar e confirmar" }).click();
  await expect(page.getByText("Perfil salvo e confirmado.")).toBeVisible();
  await page.route("**/jobs/search", (route) => route.request().method() === "OPTIONS"
    ? route.continue()
    : route.fulfill({ headers: { "access-control-allow-origin": "http://localhost:13000" }, json: {
      jobs: [],
      needs_review: [{ job: { source: "Fonte teste", title: "Backend Junior", company: "Empresa fictícia", url: "https://example.com/review" }, reason: "REGION_UNKNOWN" }],
      reports: [
        { source: "Fonte teste", status: "OK", count: 1 },
        { source: "Fonte indisponível", status: "ERROR", count: 0, message: "Falha ao consultar a fonte." },
      ],
    } }));
  await page.getByRole("button", { name: "Buscar vagas" }).click();
  await expect(page.getByRole("heading", { name: "Vagas para avaliar" })).toBeVisible();
  await expect(page.getByText("Localização ou elegibilidade geográfica precisa de confirmação")).toBeVisible();
  await page.getByText("Relatório das fontes").click();
  await expect(page.getByText("Fonte indisponível: ERROR · 0 vaga(s) · Falha ao consultar a fonte.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Buscar vagas" })).toBeEnabled();
});
