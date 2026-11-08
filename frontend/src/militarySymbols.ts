/** Simbologia VETORIAL didática inspirada na estrutura pública MD33-M-02/MD33-C-01.
 * NÃO é reprodução oficial, certificada ou completa do catálogo.
 * Os símbolos são criados do zero, em SVG, para organizações fictícias.
 * Sem acesso externo, imagens copiadas, licença de assets ou fonte remota.
 */
export type Party = "azul" | "vermelha";
export type UnitKind = "infantry" | "logistics" | "command";
export type Echelon = "platoon" | "company" | "battalion" | "brigade";
export type SimUnit = {
  id:string;
  party:Party;
  name:string;
  x:number;
  y:number;
  kind?:UnitKind;
  echelon?:Echelon;
};

export const MILITARY_SYMBOL_REFERENCE = {
  title: "Simbologia militar terrestre — protótipo didático",
  catalog: "MD33-C-01 (1ª edição, 2021)",
  status: "composição ilustrativa, sem declaração de conformidade oficial",
} as const;

const ECHELON_MARK: Record<Echelon,string> = {
  platoon:"•••",
  company:"I",
  battalion:"II",
  brigade:"X",
};

export function symbolMarkup(party:Party, kind:UnitKind, echelon:Echelon):string {
  const hostile = party === "vermelha";
  const stroke = hostile ? "#9f343b" : "#235697";
  const fill = hostile ? "#f7dcdb" : "#dceaff";
  // Componentes geométricos didáticos. O "X" para infantaria é familiar,
  // mas o conjunto não reivindica equivalência ao símbolo oficial.
  const center = kind==="infantry"
    ? '<path d="M30 25 L68 52 M68 25 L30 52" stroke-width="4.3" stroke-linecap="round"/>'
    : kind==="logistics"
      ? '<path d="M34 40 L43 49 L61 29" stroke-width="4.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
      : '<path d="M31 28 H67 M49 23 V54" stroke-width="4" stroke-linecap="round"/>';
  const mark = ECHELON_MARK[echelon];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 98 82" role="img" aria-hidden="true">
    <text x="49" y="13" font-size="13" font-weight="800" font-family="Arial,sans-serif"
      text-anchor="middle" fill="${stroke}">${mark}</text>
    <rect x="13" y="18" width="72" height="44" rx="2" fill="${fill}" stroke="${stroke}" stroke-width="3"/>
    <g stroke="${stroke}" fill="none">${center}</g>
    <path d="M13 62 V69" stroke="${stroke}" stroke-width="2" opacity=".6"/>
  </svg>`;
}

export function createUnitMarker(unit:SimUnit):HTMLElement {
  const wrapper=document.createElement("div");
  wrapper.className="military-unit-marker";
  wrapper.setAttribute("role","img");
  wrapper.setAttribute("aria-label", `Símbolo didático de ${unit.name}`);
  wrapper.title=unit.name;
  const echelon=unit.echelon ?? "company";
  const kind=unit.kind ?? "infantry";
  wrapper.innerHTML=symbolMarkup(unit.party,kind,echelon);
  return wrapper;
}
