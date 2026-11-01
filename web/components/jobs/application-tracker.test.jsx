import { expect, test } from "bun:test";
import { renderToStaticMarkup } from "react-dom/server";
import { ApplicationTracker } from "./application-tracker";

test("shows a loading state while the application tracker is restored", () => {
  const html = renderToStaticMarkup(<ApplicationTracker profileId="synthetic" refreshKey={0} onView={() => {}} />);
  expect(html).toContain("Acompanhamento de vagas");
  expect(html).toContain("Carregando acompanhamento");
});
