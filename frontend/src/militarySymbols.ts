/** Catálogo vetorial DIDÁTICO e original, não homologado pela simbologia EB.
 * Referências de estudo: MD33-M-02 e MD33-C-01. Não exporta códigos SIDC.
 */
export type Party = "azul" | "vermelha";
export type UnitKind = "infantry" | "logistics" | "command" | "engineering" | "communications" | "medical" | "transport";
export type Echelon = "platoon" | "company" | "battalion" | "brigade";
export type SimUnit = {
  id:string;
  party:Party;
  name:string;
  x:number;
  y:number;
  kind?:UnitKind;
  echelon?:Echelon;
  readiness?:number;
  readiness_status?:"disponivel"|"atencao"|"indisponivel";
  available_for_simulated_actions?:boolean;
};
export const MILITARY_SYMBOL_REFERENCE = {
  title:"Biblioteca vetorial didática de organizações fictícias",
  catalog:"MD33-C-01 (2021), referência para verificação posterior",
  status:"não certificado como simbologia militar oficial",
} as const;

export const KIND_LABELS:Record<UnitKind,string> = {
  infantry:"Infantaria",
  logistics:"Logística",
  command:"Comando",
  engineering:"Engenharia",
  communications:"Comunicações",
  medical:"Saúde",
  transport:"Transporte",
};
export const ECHELON_LABELS:Record<Echelon,string> = {
  platoon:"Pelotão",
  company:"Companhia",
  battalion:"Batalhão",
  brigade:"Brigada",
};
export const PARTY_LABELS:Record<Party,string> = {
  azul:"Azul",
  vermelha:"Vermelho",
};
const ECHELON_MARK:Record<Echelon,string> = {
  platoon:"•••", company:"I", battalion:"II", brigade:"X",
};
const KIND_ICON:Record<UnitKind,string> = {
  infantry:'<path d="M30 25 L68 52 M68 25 L30 52" stroke-width="4.2" stroke-linecap="round"/>',
  logistics:'<path d="M34 41 L43 50 L61 30" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>',
  command:'<path d="M31 30 H67 M49 23 V53" stroke-width="4" stroke-linecap="round"/>',
  engineering:'<path d="M30 48 L42 27 L54 48 M55 25 V52 M64 25 V52" stroke-width="3.7" stroke-linecap="round"/>',
  communications:'<circle cx="49" cy="40" r="5" stroke-width="3"/><path d="M39 31 Q49 18 59 31 M34 27 Q49 8 64 27 M39 49 Q49 62 59 49" stroke-width="2.8" stroke-linecap="round"/>',
  medical:'<path d="M45 26 H53 V36 H63 V44 H53 V54 H45 V44 H35 V36 H45 Z" stroke-width="2.8"/>',
  transport:'<rect x="32" y="31" width="34" height="17" rx="2" stroke-width="3"/><circle cx="41" cy="52" r="4" stroke-width="2.8"/><circle cx="58" cy="52" r="4" stroke-width="2.8"/>',
};
export function safeKind(value?:string):UnitKind {
  return value && Object.prototype.hasOwnProperty.call(KIND_LABELS,value) ? value as UnitKind : "infantry";
}
export function safeEchelon(value?:string):Echelon {
  return value && Object.prototype.hasOwnProperty.call(ECHELON_LABELS,value) ? value as Echelon : "company";
}
export function symbolMarkup(party:Party, kind:UnitKind, echelon:Echelon):string {
  const red=party==="vermelha";
  const stroke=red?"#9f343b":"#235697";
  const fill=red?"#f7dcdb":"#dceaff";
  const mark=ECHELON_MARK[safeEchelon(echelon)];
  const center=KIND_ICON[safeKind(kind)];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 98 82" aria-hidden="true">
    <text x="49" y="13" font-size="13" font-weight="800" font-family="Arial,sans-serif"
      text-anchor="middle" fill="${stroke}">${mark}</text>
    <rect x="13" y="18" width="72" height="44" rx="2" fill="${fill}" stroke="${stroke}" stroke-width="3"/>
    <g stroke="${stroke}" fill="none">${center}</g>
    <path d="M13 62 V69" stroke="${stroke}" stroke-width="2" opacity=".6"/>
  </svg>`;
}
export function unitDescription(unit:SimUnit):string {
  return `${unit.name} — ${KIND_LABELS[safeKind(unit.kind)]}, ${ECHELON_LABELS[safeEchelon(unit.echelon)]}, partido ${PARTY_LABELS[unit.party]}`;
}
export function readinessInfo(unit:SimUnit):{value:number;status:"disponivel"|"atencao"|"indisponivel";label:string}{
  const n=typeof unit.readiness==="number"&&Number.isFinite(unit.readiness)
    ?Math.round(Math.max(0,Math.min(100,unit.readiness))):100;
  const status=n<=25?"indisponivel":n<=50?"atencao":"disponivel";
  return {value:n,status,label:status==="indisponivel"?"INDISPONÍVEL":status==="atencao"?"ATENÇÃO":"DISPONÍVEL"};
}
export function createUnitMarker(unit:SimUnit):HTMLElement {
  const wrapper=document.createElement("div");
  wrapper.className="military-unit-marker";
  wrapper.setAttribute("role","img");
  wrapper.setAttribute("aria-label",unitDescription(unit));
  wrapper.title=unitDescription(unit);
  // Campos não confiáveis não são interpolados como HTML. Apenas enums validados.
  const readiness=readinessInfo(unit);
  wrapper.classList.add("readiness-"+readiness.status);
  wrapper.setAttribute("aria-label",unitDescription(unit)+`, índice didático ${readiness.value}%, ${readiness.label}`);
  wrapper.innerHTML=symbolMarkup(unit.party,safeKind(unit.kind),safeEchelon(unit.echelon))+
    `<span class="unit-readiness-badge" aria-hidden="true">${readiness.value}%</span>`+
    `<span class="unit-readiness-track" aria-hidden="true"><span style="width:${readiness.value}%"></span></span>`;
  return wrapper;
}
