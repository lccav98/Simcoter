import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

type Resource = "suprimentos" | "manutencao" | "transporte" | "saude";
type Unit = {id:string;party:"azul"|"vermelha";name:string;x:number;y:number};
type Feature = {id:string;name:string;kind:string;status:"proposed"|"approved"};
type Report = {id:string;party:string;source:string;message:string;turn:number;time:string};
type Event = {kind:string;turn:number;name?:string;cause?:string;resource?:string;effect?:number};
type Session = {id:string;title:string;turn:number;seed:number;resources:Record<Resource,number>;units:Unit[];features:Feature[];reports:Report[];events:Event[]};
type APA = {turns:number;report_count:number;approved_features:number;resource_variations:Record<string,number>;events:Event[];methodology:string;recommendations:string[]};
async function request<T>(url:string, method="GET", body?:unknown):Promise<T> {
  const response = await fetch(url, {method,headers:{"Content-Type":"application/json"},body:body===undefined?undefined:JSON.stringify(body)});
  if(!response.ok){let msg="Erro na solicitação";try{const e=await response.json();msg=e.detail??msg}catch{}throw new Error(msg)}
  return response.json() as Promise<T>;
}
function Map({data}:{data:Session}){
 const blue=data.features.find(f=>f.id==="area-azul")?.status==="approved";
 const point=data.features.find(f=>f.id==="ponto-1")?.status==="approved";
 return <svg className="terrain" viewBox="0 0 640 345" role="img" aria-label="Mapa esquemático fictício com unidades e medidas aprovadas">
   <rect width="640" height="345" fill="#dce5d1"/>
   <path d="M0 80 Q120 30 230 100 T480 85 T640 100 M0 300 Q180 248 305 285 T640 255" stroke="#acc3a1" strokeWidth="54" fill="none"/>
   <path d="M370 0 Q305 100 354 170 T390 345" fill="none" stroke="#8dbbd0" strokeWidth="24"/>
   <path d="M0 170 L640 130" stroke="#cfbd91" strokeWidth="18"/>
   <path d="M0 170 L640 130" stroke="#f3e6c4" strokeWidth="11"/>
   {blue&&<path d="M40 35 L297 42 L288 312 L40 304 Z" stroke="#225fa9" strokeWidth="3" strokeDasharray="12 7" fill="#427bbd" fillOpacity=".12"/>}
   {point&&<><circle cx="305" cy="233" r="16" stroke="#8b6b35" strokeWidth="3" fill="#ffe3a5"/><text x="305" y="238" textAnchor="middle" fontSize="13">P1</text></>}
   {data.units.map(u=><g key={u.id} transform={`translate(${u.x*6.4},${u.y*3.45})`}>
     <rect x="-25" y="-16" width="50" height="32" rx="2" fill={u.party==="azul"?"#b5d3f3":"#ebc1be"} stroke={u.party==="azul"?"#235d9c":"#a3504c"} strokeWidth="3"/>
     <text textAnchor="middle" dominantBaseline="middle" fontSize="15" fontWeight="bold" fill="#17303d">{u.party==="azul"?"I":"II"}</text>
   </g>)}
   <text x="12" y="333" fontSize="13" fill="#435b42">Cenário fictício • Sem escala ou coordenadas reais</text>
 </svg>
}
function App(){
 const [data,setData]=useState<Session|null>(null);
 const [apa,setApa]=useState<APA|null>(null);
 const [source,setSource]=useState("E4 fictício");
 const [message,setMessage]=useState("");
 const [party,setParty]=useState("azul");
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 useEffect(()=>{const id=localStorage.getItem("simcoter-session");if(id)request<Session>(`/api/sessions/${id}`).then(setData).catch(()=>localStorage.removeItem("simcoter-session"))},[]);
 async function apply(action:()=>Promise<Session>){setBusy(true);setError("");try{const next=await action();setData(next);setApa(null);localStorage.setItem("simcoter-session",next.id)}catch(e){setError(String(e))}finally{setBusy(false)}}
 const create=()=>apply(()=>request("/api/sessions","POST",{title:"Exercício Horizonte",seed:2026}));
 const turn=()=>data&&apply(()=>request(`/api/sessions/${data.id}/turns`,"POST"));
 const approve=(id:string)=>data&&apply(()=>request(`/api/sessions/${data.id}/features/${id}/approve`,"POST"));
 const report=()=>{if(!data||!message.trim())return;apply(()=>request(`/api/sessions/${data.id}/reports`,"POST",{source,message,party}));setMessage("")};
 const loadApa=async()=>{if(data){setError("");try{setApa(await request(`/api/sessions/${data.id}/apa`))}catch(e){setError(String(e))}}};
 return <main className="app">
  <header className="top"><div><small>Protótipo educacional local · v0.1</small><h1>SIMCOTER</h1><p>Sistema Integrado de Modelagem e Condução de Operações Terrestres</p></div><button onClick={create} disabled={busy}>{data?"Nova partida":"Iniciar exercício"}</button></header>
  {!data?<section className="panel"><h2>Exercício Horizonte</h2><p>Uma experiência inicial com mapa fictício, registro de informações, turnos e análise de resultados. Este protótipo ainda não possui IA, multijogador ou doutrina integrada.</p><button onClick={create}>Criar partida individual</button></section>:
   <div className="layout"><section className="panel mapPanel"><div className="heading"><h2>{data.title}</h2><span>Turno {data.turn}/20</span></div><Map data={data}/><div className="legend"><span>■ Azul</span><span>■ Vermelho</span><span>Medidas aprovadas aparecem no mapa</span></div><h3>Medidas propostas</h3>{data.features.map(f=><div className="feature" key={f.id}><span>{f.name} <small>({f.status==="approved"?"aprovada":"proposta"})</small></span><button disabled={busy||f.status==="approved"} onClick={()=>approve(f.id)}>Aprovar</button></div>)}</section>
    <aside className="panel"><h2>Indicadores logísticos fictícios</h2>{Object.entries(data.resources).map(([name,val])=><div className="indicator" key={name}><label>{name} <strong>{val}/100</strong></label><div className="bar"><div style={{width:`${val}%`}}/></div></div>)}<button disabled={busy||data.turn>=20} onClick={turn}>Avançar turno</button><p className="muted">Eventos com causa registrada e regras reproduzíveis. Os índices não representam capacidades militares reais.</p></aside>
    <section className="panel"><h2>Informações do Estado-Maior fictício</h2><div className="form"><label>Origem<input value={source} maxLength={120} onChange={e=>setSource(e.target.value)}/></label><label>Partido<select value={party} onChange={e=>setParty(e.target.value)}><option value="azul">Azul</option><option value="vermelha">Vermelho</option><option value="instrutor">Instrutor</option></select></label><label>Relatório<textarea value={message} maxLength={1000} onChange={e=>setMessage(e.target.value)} placeholder="Registre um acontecimento ou informação fictícia"/></label><button disabled={busy||!message.trim()||!source.trim()} onClick={report}>Registrar relatório</button></div><div className="timeline">{data.reports.slice().reverse().map(r=><article key={r.id}><b>{r.source}</b> · {r.party} · turno {r.turn}<p>{r.message}</p></article>)}</div></section>
    <section className="panel"><h2>Histórico e Análise Pós-Ação</h2><button onClick={loadApa}>Gerar APA descritiva</button>{apa&&<div className="apa"><p><strong>{apa.turns}</strong> turnos · <strong>{apa.report_count}</strong> relatórios · <strong>{apa.approved_features}</strong> medidas aprovadas</p><h3>Alterações de indicadores</h3>{Object.entries(apa.resource_variations).map(([k,v])=><p key={k}>{k}: −{v}</p>)}<p className="muted">{apa.methodology}</p>{apa.recommendations.map(x=><p key={x}>• {x}</p>)}</div>}<h3>Últimos eventos</h3><div className="timeline">{data.events.slice(-7).reverse().map((e,i)=><article key={i}><b>Turno {e.turn}</b> — {e.name??e.kind}{e.cause&&<p>{e.cause}</p>}</article>)}</div></section>
   </div>}
  {error&&<p className="error" role="alert">{error}</p>}<footer>SIMCOTER · Dados, organizações e resultados exclusivamente fictícios · Sem função de comando e controle real</footer>
 </main>
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
