import { test, expect } from "@playwright/test";
import { parseLocalPack } from "../src/localMapPack";
const pack = {
  version: 1, fictional: true, offlineAllowed: true,
  title: "Grade de teste", source: "Desenho original", license: "Uso privado",
  attribution: "Exemplo fictício",
  data: {type: "FeatureCollection", features: [{
    type: "Feature", properties: {html: "<script>bad</script>"},
    geometry: {type: "LineString", coordinates: [[-48,-15.8],[-47.9,-15.7]]},
  }]},
};
test("valida licença e limites e descarta propriedades arbitrárias", () => {
  expect(parseLocalPack(JSON.stringify(pack)).data.features[0].properties).toEqual({});
  for (const override of [{license:""}, {offlineAllowed:false}, {fictional:false}, {version:2},
    {data:{type:"FeatureCollection",features:[]}}]) {
    expect(()=>parseLocalPack(JSON.stringify({...pack,...override}))).toThrow();
  }
  const invalid=structuredClone(pack);
  invalid.data.features[0].geometry.coordinates[0]=[999,90];
  expect(()=>parseLocalPack(JSON.stringify(invalid))).toThrow();
  expect(()=>parseLocalPack("x".repeat(1_000_001))).toThrow();
});
test("instrutor importa e remove pacote sem upload", async ({page}) => {
  const uploads:string[]=[];
  page.on("request",r=>{if(r.method()==="POST")uploads.push(r.url());});
  await page.goto("/");
  await page.getByRole("button",{name:"Criar partida individual"}).click();
  await expect(page.locator(".military-unit-marker")).toHaveCount(3);
  uploads.length=0;
  await page.getByLabel("Importar pacote cartográfico fictício").setInputFiles({
    name:"teste.json",mimeType:"application/json",buffer:Buffer.from(JSON.stringify(pack)),
  });
  await expect(page.getByText("Grade de teste",{exact:true})).toBeVisible();
  await expect(page.getByText("Atribuição: Exemplo fictício")).toBeVisible();
  await page.getByRole("button",{name:"Remover pacote local"}).click();
  await expect(page.getByText("Grade de teste",{exact:true})).toHaveCount(0);
  expect(uploads).toEqual([]);
});
