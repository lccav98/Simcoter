import PdfPreview from "./PdfPreview";
import {useState} from "react";
type PlannedUnit={id:string;name:string;party:"azul"|"vermelha";parent?:string;kind?:string;echelon?:string;x:number;y:number;readiness?:number};
type Information={category:string;description:string;source:string;validity:string;certainty:string};
type Document={revision:number;status?:string;gaps?:string[];objective:string;situation:string;instructions:string;constraints:string;support:string;coordination:string;units:PlannedUnit[];information:Information[]};
const fields=[["objective","Objetivo pedagógico"],["situation","Situação inicial fictícia"],["instructions","Instruções do exercício"],["constraints","Premissas e restrições"],["support","Apoio e recursos abstratos"],["coordination","Coordenação e responsabilidades"]] as const;
const categories=[["terreno","Terreno"],["clima","Condições meteorológicas"],["adversario","Adversário fictício"],["civis","Condicionantes civis"]];
export default function Preparation({sessionId,initial,units,turn,onSave}:{sessionId:string;initial?:Document;units:PlannedUnit[];turn:number;onSave:(body:unknown)=>Promise<void>}) {
 const [form,setForm]=useState<Document>(initial??{revision:0,objective:"",situation:"",instructions:"",constraints:"",support:"",coordination:"",
 units:units.map(u=>({...u,parent:u.parent??"",kind:u.kind??"logistics",echelon:u.echelon??"company",readiness:u.readiness??100})),
 information:categories.map(([category])=>({category,description:"",source:"",validity:"",certainty:"lacuna"}))});
 const [busy,setBusy]=useState(false),[error,setError]=useState("");
 const updateUnit=(index:number,patch:Partial<PlannedUnit>)=>setForm(f=>({...f,units:f.units.map((u,i)=>i===index?{...u,...patch}:u)}));
 async function save(action:string) {
  setBusy(true);setError("");
  try {const {status,gaps,...payload}=form;
   await onSave({revision:form.revision,objective:form.objective,situation:form.situation,instructions:form.instructions,constraints:form.constraints,support:form.support,coordination:form.coordination,information:form.information,fictional:true,action,units:form.units.map(({id,name,party,parent,kind,echelon,x,y,readiness})=>({id,name,party,parent:parent??"",kind,echelon,x,y,readiness}))});
  } catch(e){setError(String(e))} finally {setBusy(false)}
 }
 return <section className="panel"><PdfPreview sessionId={sessionId} locked={turn>0||busy} onTransfer={(field,text)=>{
   const merged=[form[field],text].filter(Boolean).join("\n\n");
   if(merged.length>3000)return "O campo excederia 3.000 caracteres. Reduza o trecho ou edite o campo; nada foi substituído.";
   setForm({...form,[field]:merged,status:"draft"});return undefined;
 }}/><h2>Preparar exercício</h2>
 <p>Documentação inicial e meios exclusivamente fictícios. Revisão documental, sem análise operacional validada. A aprovação substitui as unidades do cenário antes do primeiro turno.</p>
 <p>Revisão {form.revision} · {form.status==="approved"?"Aprovada": "Rascunho"} · Visível somente ao instrutor.</p>
 {turn>0&&<p>Preparação inicial bloqueada: a simulação já começou.</p>}
 <fieldset disabled={busy||turn>0}>
 {fields.map(([key,label])=><label key={key} style={{display:"block"}}>{label}<textarea aria-label={label} maxLength={3000} value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})}/></label>)}
 <h3>Composição dos meios fictícios</h3>
 {form.units.map((u,i)=><fieldset key={u.id}><legend>Unidade {i+1}</legend>
 <label>Nome da unidade {i+1}<input maxLength={120} value={u.name} onChange={e=>updateUnit(i,{name:e.target.value})}/></label>
 <label>Partido {i+1}<select value={u.party} onChange={e=>updateUnit(i,{party:e.target.value as PlannedUnit["party"],parent:""})}><option value="azul">Azul</option><option value="vermelha">Vermelho</option></select></label>
 <label>Subordinação {i+1}<select value={u.parent??""} onChange={e=>updateUnit(i,{parent:e.target.value})}><option value="">Sem superior</option>{form.units.filter(v=>v.id!==u.id&&v.party===u.party).map(v=><option key={v.id} value={v.id}>{v.name}</option>)}</select></label>
 <label>Natureza {i+1}<select value={u.kind} onChange={e=>updateUnit(i,{kind:e.target.value})}>{[["infantry","Infantaria"],["logistics","Logística"],["command","Comando"],["engineering","Engenharia"],["communications","Comunicações"],["medical","Saúde"],["transport","Transporte"]].map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></label>
 <label>Escalão {i+1}<select value={u.echelon} onChange={e=>updateUnit(i,{echelon:e.target.value})}>{[["company","Companhia"],["battalion","Batalhão"],["brigade","Brigada"]].map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></label>
 {(["x","y","readiness"] as const).map(k=><label key={k}>{k==="readiness"?"Prontidão abstrata":k.toUpperCase()} {i+1}<input type="number" min={0} max={100} value={u[k]??100} onChange={e=>updateUnit(i,{[k]:Number(e.target.value)})}/></label>)}
 <button type="button" disabled={form.units.length===1} onClick={()=>setForm({...form,units:form.units.filter(v=>v.id!==u.id).map(v=>({...v,parent:v.parent===u.id?"":v.parent}))})}>Remover unidade {i+1}</button>
 </fieldset>)}
 <button type="button" disabled={form.units.length>=50} onClick={()=>setForm({...form,units:[...form.units,{id:crypto.randomUUID(),name:"Nova unidade fictícia",party:"azul",parent:"",kind:"logistics",echelon:"company",x:50,y:50,readiness:100}]})}>Adicionar unidade fictícia</button>
 <h3>Quadro de informações do exercício</h3><p>Registro estruturado dos quatro fatores. Hipóteses e lacunas permanecem identificadas; o sistema não infere ações ou capacidades.</p>
 {form.information.map((item,i)=><fieldset key={i}><legend>{categories.find(c=>c[0]===item.category)?.[1]}</legend>
 {(["description","source","validity"] as const).map((key)=><label key={key}>{({description:"Descrição",source:"Fonte",validity:"Validade / momento do cenário"})[key]} — {item.category}<textarea maxLength={key==="description"?2000:key==="source"?300:120} value={item[key]} onChange={e=>setForm({...form,information:form.information.map((v,j)=>i===j?{...v,[key]:e.target.value}:v)})}/></label>)}
 <label>Classificação — {item.category}<select value={item.certainty} onChange={e=>setForm({...form,information:form.information.map((v,j)=>i===j?{...v,certainty:e.target.value}:v)})}><option value="fato_do_cenario">Fato fornecido pelo cenário</option><option value="hipotese">Hipótese</option><option value="lacuna">Lacuna conhecida</option></select></label>
 </fieldset>)}
 <button onClick={()=>void save("draft")}>Salvar rascunho</button>
 <button onClick={()=>void save("approve")}>Aprovar e aplicar ao cenário fictício</button>
 </fieldset>
 {form.gaps?.map((gap,i)=><p key={i}>{gap}</p>)}{error&&<p role="alert">{error}</p>}
 </section>;
}
