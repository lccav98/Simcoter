import {test,expect} from "@playwright/test";
test("PDF sintético abre por página e não modifica unidades",async({page})=>{
 await page.goto("/");
 await page.getByRole("button",{name:"Criar partida individual"}).click();
 await page.getByRole("button",{name:"Já salvei as credenciais"}).click();
 await page.getByRole("button",{name:"Planejamento",exact:true}).click();
 await page.getByRole("button",{name:"Carregar exemplo sintético"}).click();
 await expect(page.getByText("Página 1",{exact:true})).toBeVisible();
 await expect(page.getByText("Página 2",{exact:true})).toBeVisible();
 await page.getByText("Página 1",{exact:true}).click();
 await expect(page.locator("pre")).toContainText(["Equipe Aurora"]);
 await expect(page.getByLabel("Nome da unidade 1",{exact:true})).toHaveValue("Unidade fictícia Azul 1");
 await page.getByRole("button",{name:"Descartar prévia PDF"}).click();
 await expect(page.getByText("Página 1",{exact:true})).toHaveCount(0);
});

test("trecho revisado preserva texto e persiste somente ao salvar",async({page})=>{
 await page.goto("/");
 await page.getByRole("button",{name:"Criar partida individual"}).click();
 await page.getByRole("button",{name:"Já salvei as credenciais"}).click();
 await page.getByRole("button",{name:"Planejamento",exact:true}).click();
 await page.getByLabel("Situação inicial fictícia",{exact:true}).fill("Texto original preservado.");
 await page.getByRole("button",{name:"Carregar exemplo sintético"}).click();
 await page.getByText("Página 1",{exact:true}).click();
 await page.getByRole("button",{name:"Revisar trecho da página 1",exact:true}).click();
 await page.getByLabel("Trecho revisado",{exact:true}).fill("Equipe Aurora: referência fictícia para conferência.");
 await page.getByRole("button",{name:"Acrescentar ao rascunho",exact:true}).click();
 const field=page.getByLabel("Situação inicial fictícia",{exact:true});
 await expect(field).toHaveValue(/Texto original preservado\./);
 await expect(field).toHaveValue(/PDF revisado, página 1/);
 await page.getByRole("button",{name:"Salvar rascunho",exact:true}).click();
 await expect(page.getByText(/Revisão 1/)).toBeVisible();
 await page.reload();
 await page.getByRole("button",{name:"Planejamento",exact:true}).click();
 await expect(field).toHaveValue(/Equipe Aurora/);
 await expect(page.getByText("Página 1",{exact:true})).toHaveCount(0);
});
