import {test,expect} from '@playwright/test';
test('proposta documental confirma área sem mudar unidades',async({page})=>{
 await page.goto('/');
 await page.getByRole('button',{name:'Criar partida individual'}).click();
 await page.getByRole('button',{name:'Planejamento',exact:true}).click();
 await page.route('**/document-preview',route=>route.fulfill({json:{pages:[{page:1,text:'AREA_EXERCICIO_WGS84: -48,-16,-47,-15'}],warning:'Documento sintético de teste'}}));
 await page.getByRole('button',{name:'Carregar exemplo sintético'}).click();
 await expect(page.getByText('Página 1: AREA_EXERCICIO_WGS84: -48,-16,-47,-15')).toBeVisible();
 const response=page.waitForResponse(r=>r.url().endsWith('/document-area/confirm'));
 await page.getByRole('button',{name:'Confirmar área no mapa'}).click();
 const state=await (await response).json();
 expect(state.document_area.bounds).toEqual([-48,-16,-47,-15]);
 expect(state.units[0].x).toBe(23);
 await expect(page.getByText('Área confirmada e salva. Unidades não foram reposicionadas.')).toBeVisible();
});
