import { test, expect } from "@playwright/test";

test("fluxo integrado: criar, MapLibre, EMV, turno e APA", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "SIMCOTER" })).toBeVisible();
  await page.getByRole("button", { name: "Criar partida individual" }).click();
  await expect(page.getByText("Papel: instrutor")).toBeVisible();
  await expect(page.getByText("Turno 0/20")).toBeVisible();

  // A criação da instância MapLibre independe da disponibilidade dos tiles OSM.
  // Em ambientes de CI sem WebGL, o app deve informar a indisponibilidade.
  const map = page.getByRole("application", { name: "Mapa geográfico interativo MapLibre GL JS" });
  await expect(map).toBeVisible();
  const hasCanvas = await page.locator(".maplibregl-canvas").count();
  if (hasCanvas) {
    await expect(page.locator(".maplibregl-ctrl-zoom-in")).toBeVisible();
    await expect(page.locator(".maplibregl-ctrl-zoom-out")).toBeVisible();
    await expect(page.locator(".maplibregl-ctrl-scale")).toBeVisible();
    await expect(page.locator(".military-unit-marker")).toHaveCount(3);
    await expect(page.locator(".military-unit-marker svg").first()).toBeVisible();
  } else {
    await expect(page.getByText("Este navegador não disponibiliza WebGL para o MapLibre.")).toBeVisible();
  }

  await page.getByRole("button", { name: "Já salvei as credenciais" }).click();
  await page.getByRole("button", { name: "Avançar turno" }).click();
  await expect(page.getByText("Turno 1/20")).toBeVisible();

  await page.getByRole("button", { name: "Estado-Maior", exact: true }).click();
  await page.getByRole("button", { name: "Solicitar análise" }).click();
  await expect(page.getByText("E1 — Conferência administrativa de pessoal")).toBeVisible();
  await page.getByRole("button", { name: "Aprovar", exact: true }).last().click();
  await expect(page.getByText(/Aprovadas: 1/)).toBeVisible();

  await page.getByRole("button", { name: "Avaliação e biblioteca" }).click();
  await page.getByRole("button", { name: "Gerar APA descritiva" }).click();
  await expect(page.getByText(/1 turnos/)).toBeVisible();
  await page.getByRole("button", { name: "Estado-Maior", exact: true }).click();
  await page.getByRole("button", { name: "Consultar tutor" }).click();
  await expect(page.getByText("Modo sem IA")).toBeVisible();
});

test("acesso separado por partido não revela dados globais", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Criar partida individual" }).click();

  const id = await page.locator("code").first().innerText();
  const redToken = await page.locator(".token").nth(2).innerText();

  await page.getByRole("button", { name: "Sair da sessão" }).click();
  await page.getByLabel("Identificador da partida").fill(id);
  await page.getByLabel("Token do participante").fill(redToken);
  await page.getByRole("button", { name: "Entrar", exact: true }).click();

  await expect(page.getByText("Papel: vermelha")).toBeVisible();
  await expect(page.getByText("Motor probabilístico · MPS")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Estado-Maior", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Avançar turno" })).toHaveCount(0);
});
