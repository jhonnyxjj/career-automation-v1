import { expect, test } from "bun:test";
import { renderToStaticMarkup } from "react-dom/server";
import { ProfileEditor } from "./profile-editor";

test("shows extracted facts for review and allows adding profile sections", () => {
  const profile = {
    id: "synthetic", personal: { name: "Pessoa Teste", headline: "Backend" },
    professional_summary: "Resumo fictício", technical_skills: [{ category: "Linguagens", items: ["TypeScript"] }],
    experiences: [], projects: [], education: [],
  };
  const html = renderToStaticMarkup(<ProfileEditor profile={profile} onSaved={() => {}} onCancel={() => {}} />);
  expect(html).toContain("Pessoa Teste");
  expect(html).toContain("Resumo fictício");
  expect(html).toContain("Adicionar experiência");
  expect(html).toContain("Salvar e confirmar");
});
