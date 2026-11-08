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


test("legenda: filtros por partido, natureza e medidas", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Criar partida individual" }).click();
  await page.getByRole("button", { name: "Legenda e camadas" }).click();
  const legend=page.getByRole("region", { name: "Legenda e filtros cartográficos" });
  await expect(legend).toBeVisible();
  await expect(legend.getByText("3 de 3 unidades exibidas")).toBeVisible();
  await expect(legend.locator(".symbolLegendItem")).toHaveCount(3);
  await legend.getByRole("checkbox", { name: "Vermelho" }).uncheck();
  await expect(legend.getByText("2 de 3 unidades exibidas")).toBeVisible();
  await legend.getByRole("checkbox", { name: "Logística" }).uncheck();
  await expect(legend.getByText("1 de 3 unidades exibidas")).toBeVisible();
  await legend.getByRole("checkbox", { name: "Medidas gráficas aprovadas" }).uncheck();
  await expect(legend.getByRole("checkbox", { name: "Medidas gráficas aprovadas" })).not.toBeChecked();
  const markers=page.locator(".military-unit-marker");
  // Sem WebGL, a legenda ainda mantém sua utilidade; os marcadores exigem a renderização.
  if(await page.locator(".maplibregl-canvas").count() > 0) {
    await expect(markers).toHaveCount(1);
  }
  await legend.getByRole("checkbox", { name: "Vermelho" }).check();
  await legend.getByRole("checkbox", { name: "Logística" }).check();
  await expect(legend.getByText("3 de 3 unidades exibidas")).toBeVisible();
  await page.getByRole("button", { name: "Ocultar legenda" }).click();
  await expect(legend).toHaveCount(0);
});


test("som opcional: desativado por padrão, volume e prévia sem alterar partida", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Criar partida individual" }).click();
  const turn=page.getByText("Turno 0/20");
  await expect(turn).toBeVisible();
  const sound=page.getByRole("button", { name: "Ativar áudio" });
  await expect(sound).toHaveAttribute("aria-pressed","false");
  await expect(page.getByRole("button", { name: "Ouvir prévia de embate fictício" })).toBeDisabled();
  await sound.click();
  await expect(page.getByRole("button", { name: "Silenciar áudio" })).toHaveAttribute("aria-pressed","true");
  const volume=page.getByRole("slider", { name: "Volume dos efeitos sonoros" });
  await volume.focus();
  await volume.press("Home");
  await volume.press("ArrowRight");
  await expect(page.getByText("Volume: 1%")).toBeVisible();
  await page.getByRole("button", { name: "Ouvir prévia de embate fictício" }).click();
  await expect(page.getByText("Turno 0/20")).toBeVisible();
  await page.getByRole("button", { name: "Silenciar áudio" }).click();
  await expect(page.getByRole("button", { name: "Ativar áudio" })).toHaveAttribute("aria-pressed","false");
});


test("prontidão no calunga e regras ambientais visíveis para instrutor", async ({page}) => {
  await page.goto("/");
  await page.getByRole("button", {name:"Criar partida individual"}).click();
  await page.getByRole("button", {name:"Legenda e camadas"}).click();
  const legend=page.getByRole("region",{name:"Legenda e filtros cartográficos"});
  await expect(legend.getByText(/Índice didático: 84%/)).toBeVisible();
  await page.getByRole("button",{name:"Ocultar legenda"}).click();

  await page.getByRole("button",{name:"Reduzir prontidão fictícia de Unidade fictícia Azul 2"}).click();
  await expect(page.getByText(/45% · ATENÇÃO/)).toBeVisible();

  await page.getByRole("button",{name:"Planejamento",exact:true}).click();
  await expect(page.getByText("Terreno e clima do exercício")).toBeVisible();
  await page.getByRole("button",{name:"Verificar disponibilidade"}).click();
  await expect(page.getByText("Permitido no exercício")).toBeVisible();

  await page.getByLabel("Condição climática").selectOption("severe");
  await page.getByRole("button",{name:"Verificar disponibilidade"}).click();
  await expect(page.getByText("Bloqueado no exercício")).toBeVisible();
  await expect(page.getByText(/Suspensão climática fictícia/)).toBeVisible();

  await page.getByRole("button",{name:"Estado-Maior",exact:true}).click();
  await page.getByRole("button",{name:"Solicitar análise"}).click();
  await expect(page.getByText(/clima didático: severe/)).toBeVisible();
});
