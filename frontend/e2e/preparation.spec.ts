import {test,expect} from "@playwright/test";
test("preparação salva rascunho e biblioteca mostra fontes",async({page})=>{
 await page.goto("/");
 await page.getByRole("button",{name:"Criar partida individual"}).click();
 await page.getByRole("button",{name:"Já salvei as credenciais"}).click();
 await page.getByRole("button",{name:"Planejamento",exact:true}).click();
 await page.getByLabel("Objetivo pedagógico",{exact:true}).fill("Revisar fontes do exercício");
 await page.getByLabel("Nome da unidade 1",{exact:true}).fill("Organização fictícia de estudo");
 await page.getByRole("button",{name:"Salvar rascunho",exact:true}).click();
 await expect(page.getByText(/Revisão 1/)).toBeVisible();
 await page.getByRole("button",{name:"Salvar rascunho",exact:true}).click();
 await expect(page.getByText(/Revisão 2/)).toBeVisible();
 await page.reload();
 await page.getByRole("button",{name:"Planejamento",exact:true}).click();
 await expect(page.getByLabel("Objetivo pedagógico",{exact:true})).toHaveValue("Revisar fontes do exercício");
 await page.getByRole("button",{name:"Avaliação e biblioteca",exact:true}).click();
 await expect(page.getByRole("heading",{name:"Casos históricos para estudo"})).toBeVisible();
 await expect(page.getByRole("link",{name:"Consultar fonte de Monte Castelo"})).toBeVisible();
});
