import Mockup from "./Mockup";
import HistoricalLibrary from "./HistoricalLibrary";
import Preparation from "./Preparation";
import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import MapView, { type EnvironmentData } from "./MapView";
import { GameAudio } from "./gameAudio";

type Resource = "suprimentos" | "manutencao" | "transporte" | "saude";
type Unit = {id:string;party:"azul"|"vermelha";name:string;x:number;y:number;readiness?:number;readiness_status?:"disponivel"|"atencao"|"indisponivel";available_for_simulated_actions?:boolean};
type Feature = {id:string;name:string;kind:string;status:"proposed"|"approved"};
type Report = {id:string;party:string;source:string;message:string;turn:number;time:string};
type Event = {kind:string;turn:number;name?:string;cause?:string;resource?:string;effect?:number};
type Session = {preparation?: React.ComponentProps<typeof Preparation>["initial"];id:string;title:string;turn:number;seed?:number;role?:"instrutor"|"azul"|"vermelha";resources:Partial<Record<Resource,number>>;units:Unit[];features:Feature[];reports:Report[];events:Event[]};
type CreatedSession = {session:Session;credentials:Record<"instrutor"|"azul"|"vermelha",string>};
type APA = {turns:number;report_count:number;approved_features:number;resource_variations:Record<string,number>;weather?:string;environmental_movements?:Event[];unavailable_units?:Event[];unit_readiness?:{unit_id:string;name:string;readiness:number;status:string}[];events:Event[];methodology:string;recommendations:string[]};
type Problem = {id:string;category:string;title:string;summary:string;evidence:string[];trigger:string;question:string;rule:string};
type ContextResult = {turn:number;generation_mode:string;context_hash:string;problems:Problem[]};
type DoctrineItem = {code:string;title:string;category:string;edition_status:string;verification:string;reference_url:string};
type DoctrineResult = {items:DoctrineItem[];mode:string;verified_citations:boolean};
type StaffTask = {id:string;agent:string;agent_title:string;title:string;summary:string;status:string;turn:number;evidence_hash:string;rule:string};
type StaffView = {turn:number;adapter:string;version:string;tasks:StaffTask[];summary:{proposed:number;approved:number;rejected:number};catalog:{agents:Record<string,{title:string;responsibility:string}>}};
type AIExplanation = {mode:string;available:boolean;model:string|null;context_hash:string;summary:string;findings:{evidence_id:string;explanation:string}[];uncertainties:string[];warning?:string};
type ProbabilityResult = {model_version:string;turn:number;repetitions:number;categories:Record<string,number>;severities:Record<string,number>;average_variation:Record<string,number>;warning:string};
async function request<T>(url:string, method="GET", body?:unknown):Promise<T> {
  const response = await fetch(url, {method,headers:{"Content-Type":"application/json",...(sessionStorage.getItem("simcoter-token")?{"Authorization":`Bearer ${sessionStorage.getItem("simcoter-token")}`}:{})},body:body===undefined?undefined:JSON.stringify(body)});
  if(!response.ok){let msg="Erro na solicitação";try{const e=await response.json();msg=e.detail??msg}catch{}throw new Error(msg)}
  return response.json() as Promise<T>;
}
function App(){
 const [showMockup,setShowMockup]=useState(false);
 const [data,setData]=useState<Session|null>(null);
 const [environment,setEnvironment]=useState<EnvironmentData|null>(null);
 const [moveUnit,setMoveUnit]=useState("azul-1");
 const [destinationX,setDestinationX]=useState(40);
 const [destinationY,setDestinationY]=useState(50);
 const [movementAuthorized,setMovementAuthorized]=useState(false);
 const [movementResult,setMovementResult]=useState<{allowed:boolean;terrain:string;weather:string;reasons:string[];review_required:boolean}|null>(null);
 const audioRef=useRef<GameAudio|null>(null);
 if(!audioRef.current)audioRef.current=new GameAudio();
 const [soundEnabled,setSoundEnabled]=useState(false);
 const [soundVolume,setSoundVolume]=useState(28);
 const [audioInfo,setAudioInfo]=useState("");
 const [staff,setStaff]=useState<StaffView|null>(null);
 const [activeView,setActiveView]=useState<"situacao"|"planejamento"|"emv"|"avaliacao">("situacao");
 const [agent,setAgent]=useState("E1");
 const [newCredentials,setNewCredentials]=useState<CreatedSession["credentials"]|null>(null);
 const [joinId,setJoinId]=useState("");
 const [joinToken,setJoinToken]=useState("");
 const [apa,setApa]=useState<APA|null>(null);
 const [context,setContext]=useState<ContextResult|null>(null);
 const [doctrine,setDoctrine]=useState<DoctrineResult|null>(null);
 const [query,setQuery]=useState("");
 const [probability,setProbability]=useState<ProbabilityResult|null>(null);
 const [aiExplanation,setAiExplanation]=useState<AIExplanation|null>(null);
 const [repetitions,setRepetitions]=useState(500);
 const [source,setSource]=useState("E4 fictício");
 const [message,setMessage]=useState("");
 const [party,setParty]=useState("azul");
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 useEffect(()=>{if(data?.role==="instrutor")void request<EnvironmentData>(`/api/sessions/${data.id}/environment`).then(setEnvironment).catch(()=>setEnvironment(null));else setEnvironment(null)},[data?.id,data?.role,data?.turn,data?.events.length]);
 useEffect(()=>{audioRef.current?.configure(soundEnabled,soundVolume/100)},[soundEnabled,soundVolume]);
 useEffect(()=>()=>{void audioRef.current?.close()},[]);
 useEffect(()=>{const id=sessionStorage.getItem("simcoter-session");const token=sessionStorage.getItem("simcoter-token");if(id&&token)request<Session>(`/api/sessions/${id}`).then(setData).catch(()=>{sessionStorage.removeItem("simcoter-session");sessionStorage.removeItem("simcoter-token")})},[]);
 async function apply(action:()=>Promise<Session>){setBusy(true);setError("");try{const next=await action();setData(next);setApa(null);setMovementResult(null);setContext(null);setProbability(null);setAiExplanation(null);setStaff(null);sessionStorage.setItem("simcoter-session",next.id)}catch(e){setError(String(e))}finally{setBusy(false)}}
 const create=async()=>{setBusy(true);setError("");try{const created=await request<CreatedSession>("/api/sessions","POST",{title:"Exercício Horizonte",seed:2026});setNewCredentials(created.credentials);sessionStorage.setItem("simcoter-token",created.credentials.instrutor);sessionStorage.setItem("simcoter-session",created.session.id);setData(created.session);setApa(null);setContext(null);setProbability(null);setAiExplanation(null);setStaff(null)}catch(e){setError(String(e))}finally{setBusy(false)}};
 const join=async()=>{if(!joinId.trim()||!joinToken.trim())return;setBusy(true);setError("");try{sessionStorage.setItem("simcoter-token",joinToken.trim());const joined=await request<Session>(`/api/sessions/${encodeURIComponent(joinId.trim())}`);sessionStorage.setItem("simcoter-session",joined.id);setData(joined);setNewCredentials(null);setApa(null);setContext(null);setProbability(null);setAiExplanation(null)}catch(e){sessionStorage.removeItem("simcoter-token");setError(String(e))}finally{setBusy(false)}};
 const leave=()=>{sessionStorage.removeItem("simcoter-token");sessionStorage.removeItem("simcoter-session");setData(null);setNewCredentials(null);setApa(null);setContext(null);setProbability(null);setAiExplanation(null);setStaff(null)};
 const turn=()=>{if(!data)return;const session=data;
   // desbloqueia áudio dentro do clique, antes da resposta assíncrona da API.
   if(soundEnabled)void audioRef.current?.unlock();
   void apply(async()=>{
     const next=await request<Session>(`/api/sessions/${session.id}/turns`,"POST");
     if(soundEnabled){
       const latest=next.events[next.events.length-1];
       audioRef.current?.play(latest?.kind==="scenario_event"?"incident":"routine");
     }
     return next;
   });
 };
 const enableSound=()=>{const next=!soundEnabled;setSoundEnabled(next);
   audioRef.current?.configure(next,soundVolume/100);
   if(next)void audioRef.current?.unlock().then(ok=>setAudioInfo(ok?"Áudio ativado":"Áudio indisponível neste navegador."));
   else setAudioInfo("Áudio silenciado.");
 };
 const previewSound=()=>{if(!soundEnabled){setAudioInfo("Ative o som para ouvir a prévia.");return}
   void audioRef.current?.unlock().then(ok=>{
     if(ok){audioRef.current?.play("engagement_preview");setAudioInfo("Prévia sonora fictícia reproduzida; nenhum embate foi criado.")}
     else setAudioInfo("Áudio indisponível. Verifique as permissões do navegador.");
   });
 };
 const adjustReadiness=(unitId:string,change:number)=>data&&apply(()=>request(`/api/sessions/${data.id}/units/${unitId}/readiness`,"POST",{change}));
 const updateWeather=(weather:string)=>data&&apply(()=>request(`/api/sessions/${data.id}/environment/weather`,"POST",{weather}));
 const checkMovement=async()=>{if(!data)return;setError("");try{setMovementResult(await request(`/api/sessions/${data.id}/units/${moveUnit}/movement/check`,"POST",{x:destinationX,y:destinationY,authorized:movementAuthorized}))}catch(e){setError(String(e))}};
 const moveInExercise=()=>data&&apply(()=>request(`/api/sessions/${data.id}/units/${moveUnit}/movement`,"POST",{x:destinationX,y:destinationY,authorized:movementAuthorized}));
 const approve=(id:string)=>data&&apply(()=>request(`/api/sessions/${data.id}/features/${id}/approve`,"POST"));
 const report=()=>{if(!data||!message.trim())return;apply(()=>request(`/api/sessions/${data.id}/reports`,"POST",{source,message,...(data.role==="instrutor"?{party}:{})}));setMessage("")};
 const loadApa=async()=>{if(data){setError("");try{setApa(await request(`/api/sessions/${data.id}/apa`))}catch(e){setError(String(e))}}};
 const loadContext=async()=>{if(data){setError("");try{setContext(await request(`/api/sessions/${data.id}/context`))}catch(e){setError(String(e))}}};
 const loadStaff=async()=>{if(data){setError("");try{setStaff(await request<StaffView>(`/api/sessions/${data.id}/staff`))}catch(e){setError(String(e))}}};
 const assignStaff=async()=>{if(!data)return;setBusy(true);setError("");try{setStaff(await request<StaffView>(`/api/sessions/${data.id}/staff/tasks`,"POST",{agent}))}catch(e){setError(String(e))}finally{setBusy(false)}};
 const reviewStaff=async(taskId:string,action:string)=>{if(!data)return;setBusy(true);setError("");try{setStaff(await request<StaffView>(`/api/sessions/${data.id}/staff/tasks/${taskId}/review`,"POST",{action}))}catch(e){setError(String(e))}finally{setBusy(false)}};
 const loadAi=async()=>{if(data){setError("");setBusy(true);try{setAiExplanation(await request(`/api/sessions/${data.id}/ai/explanation`))}catch(e){setError(String(e))}finally{setBusy(false)}}};
 const loadProbability=async()=>{if(data){setError("");try{setProbability(await request(`/api/sessions/${data.id}/probability?repetitions=${repetitions}`))}catch(e){setError(String(e))}}};
 const searchDoctrine=async()=>{setError("");try{setDoctrine(await request(`/api/doctrine?q=${encodeURIComponent(query)}`))}catch(e){setError(String(e))}};
 if(showMockup)return <Mockup onExit={()=>setShowMockup(false)}/>;
 return <main className="app">
 <button onClick={()=>setShowMockup(true)}>Explorar demonstração completa</button>
  <header className="top"><div><small>Protótipo educacional local · v0.8</small><h1>SIMCOTER</h1><p>Sistema Integrado de Modelagem e Condução de Operações Terrestres</p></div><button onClick={data?leave:create} disabled={busy}>{data?"Sair da sessão":"Criar exercício"}</button></header>
  {!data?<section className="panel"><h2>Exercício Horizonte</h2><p>Crie um exercício fictício ou acesse uma partida com o identificador e token fornecidos pelo instrutor. Proteção experimental, somente para uso local.</p><button onClick={create} disabled={busy}>Criar partida individual</button><h3>Entrar em uma partida</h3><div className="form"><label>Identificador da partida<input value={joinId} onChange={e=>setJoinId(e.target.value)}/></label><label>Token do participante<input type="password" value={joinToken} onChange={e=>setJoinToken(e.target.value)}/></label><button disabled={busy||!joinId.trim()||!joinToken.trim()} onClick={join}>Entrar</button></div></section>:
   <><div className="panel"><strong>Papel: {data.role??"instrutor"}</strong> · Partida: <code>{data.id}</code>{newCredentials&&<div className="apa"><p><strong>Credenciais exibidas somente agora:</strong> copie e guarde em local seguro. Compartilhe cada token apenas com seu destinatário.</p>{Object.entries(newCredentials).map(([name,token])=><p key={name}><strong>{name}</strong> — <code className="token">{token}</code> <button onClick={()=>navigator.clipboard.writeText(token)}>Copiar token</button></p>)}<button onClick={()=>setNewCredentials(null)}>Já salvei as credenciais</button></div>}</div><nav className="workspace-nav" aria-label="Áreas do exercício"><button className={activeView==="situacao"?"selected":""} aria-current={activeView==="situacao"?"page":undefined} onClick={()=>setActiveView("situacao")}>Situação</button>{data.role==="instrutor"&&<button className={activeView==="planejamento"?"selected":""} aria-current={activeView==="planejamento"?"page":undefined} onClick={()=>setActiveView("planejamento")}>Planejamento</button>}{data.role==="instrutor"&&<button className={activeView==="emv"?"selected":""} aria-current={activeView==="emv"?"page":undefined} onClick={()=>setActiveView("emv")}>Estado-Maior</button>}<button className={activeView==="avaliacao"?"selected":""} aria-current={activeView==="avaliacao"?"page":undefined} onClick={()=>setActiveView("avaliacao")}>{data.role==="instrutor"?"Avaliação e biblioteca":"Biblioteca"}</button></nav><div className="layout"><section className="panel mapPanel"><div className="heading"><h2>{data.title}</h2><span>Turno {data.turn}/20</span></div><MapView key={data.id+data.role} allowImport={data.role==="instrutor"} units={data.units} features={data.features} environment={environment}/><div className="legend"><span>■ Azul</span><span>■ Vermelho</span><span>Controles + e − para zoom · arraste e gesto de pinça no iPad</span></div><h3>Disponibilidade das unidades fictícias</h3><p className="muted">Indicador pedagógico, não poder de combate real. 25% ou menos: unidade automaticamente indisponível para novas ações simuladas.</p>{data.units.map(u=><div className="unitStatusRow" key={u.id}><div><strong>{u.name}</strong><small className="unitStatusLabel">{u.readiness??100}% · {(u.readiness_status==="indisponivel")?"INDISPONÍVEL":u.readiness_status==="atencao"?"ATENÇÃO":"DISPONÍVEL"}</small></div>{data.role==="instrutor"&&<div className="unitStatusActions"><button disabled={busy||(u.readiness??100)<=0} onClick={()=>adjustReadiness(u.id,-20)} aria-label={`Reduzir prontidão fictícia de ${u.name}`}>−20</button><button disabled={busy||(u.readiness??100)>=100} onClick={()=>adjustReadiness(u.id,20)} aria-label={`Aumentar prontidão fictícia de ${u.name}`}>+20</button></div>}</div>)}<h3>Medidas propostas</h3>{data.features.map(f=><div className="feature" key={f.id}><span>{f.name} <small>({f.status==="approved"?"aprovada":"proposta"})</small></span>{data.role==="instrutor"&&<button disabled={busy||f.status==="approved"} onClick={()=>approve(f.id)}>Aprovar</button>}</div>)}</section>
    <section className="panel audioPanel" hidden={activeView!=="situacao"}>
      <h2>Ambiente sonoro</h2>
      <p className="muted">Efeitos sintéticos criados no próprio dispositivo. Sem áudio externo, sem gravações e sem custo por reprodução.</p>
      <div className="audioControls">
        <button type="button" aria-pressed={soundEnabled} onClick={enableSound}>
          {soundEnabled?"Silenciar áudio":"Ativar áudio"}
        </button>
        <label>Volume: {soundVolume}%
          <input type="range" min="0" max="45" step="1" value={soundVolume}
            aria-label="Volume dos efeitos sonoros" disabled={!soundEnabled}
            onChange={e=>{const n=Number(e.target.value);setSoundVolume(n);audioRef.current?.configure(soundEnabled,n/100)}}/>
        </label>
        <button type="button" onClick={previewSound} disabled={!soundEnabled}>Ouvir prévia de embate fictício</button>
      </div>
      <p className="muted" role="status" aria-live="polite">{audioInfo||"Som desativado por padrão. A prévia não cria acontecimentos na partida."}</p>
    </section>
    <aside className="panel" hidden={activeView!=="situacao"}><h2>Indicadores logísticos fictícios</h2>{Object.entries(data.resources).map(([name,val])=><div className="indicator" key={name}><label>{name} <strong>{val}/100</strong></label><div className="bar"><div style={{width:`${val}%`}}/></div></div>)}{data.role==="instrutor"&&<button disabled={busy||data.turn>=20} onClick={turn}>Avançar turno</button>}<p className="muted">Eventos com causa registrada e regras reproduzíveis. Os índices não representam capacidades militares reais.</p></aside>
    <section className="panel" hidden={activeView!=="situacao"}><h2>Informações do Estado-Maior fictício</h2><div className="form"><label>Origem<input value={source} maxLength={120} onChange={e=>setSource(e.target.value)}/></label>{data.role==="instrutor"&&<label>Destinatário<select value={party} onChange={e=>setParty(e.target.value)}><option value="azul">Azul</option><option value="vermelha">Vermelho</option><option value="instrutor">Instrutor</option></select></label>}<label>Relatório<textarea value={message} maxLength={1000} onChange={e=>setMessage(e.target.value)} placeholder="Registre um acontecimento ou informação fictícia"/></label><button disabled={busy||!message.trim()||!source.trim()} onClick={report}>Registrar relatório</button></div><div className="timeline">{data.reports.slice().reverse().map(r=><article key={r.id}><b>{r.source}</b> · {r.party} · turno {r.turn}<p>{r.message}</p></article>)}</div></section>
    {data.role==="instrutor"&&<section className="panel" hidden={activeView!=="avaliacao"}><h2>Histórico e Análise Pós-Ação</h2><button onClick={loadApa}>Gerar APA descritiva</button>{apa&&<div className="apa"><p><strong>{apa.turns}</strong> turnos · <strong>{apa.report_count}</strong> relatórios · <strong>{apa.approved_features}</strong> medidas aprovadas</p><h3>Condição final das unidades</h3>{apa.unit_readiness?.map(u=><p key={u.unit_id}>{u.name}: {u.readiness}% — {u.status}</p>)}<h3>Ambiente e restrições</h3><p>Clima final do exercício: {apa.weather??"não informado"} · mudanças/movimentos fictícios: {apa.environmental_movements?.length??0} · eventos de indisponibilidade: {apa.unavailable_units?.length??0}</p><h3>Alterações de indicadores</h3>{Object.entries(apa.resource_variations).map(([k,v])=><p key={k}>{k}: −{v}</p>)}<p className="muted">{apa.methodology}</p>{apa.recommendations.map(x=><p key={x}>• {x}</p>)}</div>}<h3>Últimos eventos</h3><div className="timeline">{data.events.slice(-7).reverse().map((e,i)=><article key={i}><b>Turno {e.turn}</b> — {e.name??e.kind}{e.cause&&<p>{e.cause}</p>}</article>)}</div></section>}
    {data.role==="instrutor"&&<div hidden={activeView!=="planejamento"}><Preparation sessionId={data.id} key={data.id+":"+ (data.preparation?.revision??0)} initial={data.preparation} units={data.units} turn={data.turn} onSave={async body=>{const next=await request<Session>('/api/sessions/'+data.id+'/preparation',"POST",body);setData(next);setMoveUnit(next.units[0]?.id??"");}}/></div>}
{data.role==="instrutor"&&<section className="panel" hidden={activeView!=="planejamento"}><h2>Terreno e clima do exercício</h2><p className="muted">Áreas abstratas do tabuleiro, não classificações da cartografia real. Ações fictícias são verificadas pelo servidor.</p><div className="form"><label>Condição climática<select aria-label="Condição climática" value={environment?.weather??"normal"} onChange={e=>updateWeather(e.target.value)}><option value="normal">Condições estáveis</option><option value="adverse">Condições adversas — requer revisão</option><option value="severe">Suspensão climática</option></select></label><label>Unidade<select aria-label="Unidade para teste de deslocamento" value={moveUnit} onChange={e=>{setMoveUnit(e.target.value);setMovementResult(null)}}>{data.units.map(u=><option key={u.id} value={u.id}>{u.name}</option>)}</select></label><div className="environmentCoords"><label>X (0–100)<input type="number" min="0" max="100" value={destinationX} onChange={e=>{setDestinationX(Number(e.target.value));setMovementResult(null)}}/></label><label>Y (0–100)<input type="number" min="0" max="100" value={destinationY} onChange={e=>{setDestinationY(Number(e.target.value));setMovementResult(null)}}/></label></div><label className="environmentCheck"><input type="checkbox" checked={movementAuthorized} onChange={e=>{setMovementAuthorized(e.target.checked);setMovementResult(null)}}/>Autorização humana para área restritiva ou clima adverso</label><div className="search"><button disabled={busy||!Number.isInteger(destinationX)||!Number.isInteger(destinationY)||destinationX<0||destinationX>100||destinationY<0||destinationY>100} onClick={checkMovement}>Verificar disponibilidade</button><button disabled={busy||!movementResult?.allowed} onClick={moveInExercise}>Aplicar deslocamento fictício</button></div></div>{movementResult&&<div className="apa" role="status"><p><strong>{movementResult.allowed?"Permitido no exercício":"Bloqueado no exercício"}</strong> · terreno {movementResult.terrain} · clima {movementResult.weather}</p>{movementResult.reasons.map(x=><p key={x}>{x}</p>)}</div>}</section>}
   {data.role==="instrutor"&&<section className="panel" hidden={activeView!=="planejamento"}><h2>Motor probabilístico · MPS</h2><p className="muted">Prévia estatística do próximo turno, com valores inventados para ensino. Não estima resultados reais de combate.</p><div className="form"><label>Repetições (1–2.000)<input type="number" min={1} max={2000} value={repetitions} onChange={e=>setRepetitions(Number(e.target.value))}/></label><button disabled={busy||data.turn>=20||repetitions<1||repetitions>2000||!Number.isInteger(repetitions)} onClick={loadProbability}>Simular possibilidades</button></div>{probability&&<div className="apa"><p><strong>{probability.repetitions.toLocaleString("pt-BR")}</strong> repetições · turno {probability.turn}</p><h3>Ocorrências por categoria</h3>{Object.entries(probability.categories).map(([name,count])=><div className="indicator" key={name}><label>{name.replace(/_/g," ")} <strong>{count} ({(100*count/probability.repetitions).toFixed(1)}%)</strong></label><div className="bar"><div style={{width:`${100*count/probability.repetitions}%`}}/></div></div>)}<h3>Severidades fictícias</h3>{Object.entries(probability.severities).map(([name,count])=><p key={name}>{name}: {count} ({(100*count/probability.repetitions).toFixed(1)}%)</p>)}<h3>Variação média dos indicadores</h3>{Object.entries(probability.average_variation).map(([key,value])=><p key={key}>{key}: {value.toLocaleString("pt-BR")} pontos</p>)}<p className="muted">{probability.warning}</p></div>}</section>}
   {data.role==="instrutor"&&<section className="panel" hidden={activeView!=="emv"}><h2>Estado-Maior Virtual · EMV</h2><p className="muted">Agentes E1–E4 produzem propostas de revisão didática. A decisão e a aprovação continuam sob responsabilidade do jogador. Paperclip permanece opcional e não instalado.</p><div className="search"><select aria-label="Agente virtual" value={agent} onChange={e=>setAgent(e.target.value)}><option value="E1">E1 — Pessoal</option><option value="E2">E2 — Informações</option><option value="E3">E3 — Planejamento</option><option value="E4">E4 — Logística</option></select><button disabled={busy} onClick={assignStaff}>Solicitar análise</button><button disabled={busy} onClick={loadStaff}>Atualizar</button></div>{staff&&<div className="timeline"><p className="muted">Coordenação: {staff.adapter} · Pendentes: {staff.summary.proposed} · Aprovadas: {staff.summary.approved} · Rejeitadas: {staff.summary.rejected}</p>{staff.tasks.slice().reverse().map(t=><article key={t.id}><b>{t.agent} — {t.title}</b><p>{t.summary}</p><p><strong>Estado:</strong> {t.status} · Turno {t.turn}</p>{t.status==="proposed"&&<div className="search"><button disabled={busy} onClick={()=>reviewStaff(t.id,"approved")}>Aprovar</button><button disabled={busy} onClick={()=>reviewStaff(t.id,"rejected")}>Rejeitar</button></div>}</article>)}</div>}</section>}
   {data.role==="instrutor"&&<section className="panel" hidden={activeView!=="emv"}><h2>Tutor com IA local</h2><p className="muted">Assessoria pedagógica por Ollama, opcional e desativada por padrão. Não altera os turnos ou as regras do jogo.</p><button disabled={busy} onClick={loadAi}>Consultar tutor</button>{aiExplanation&&<div className="apa"><p><strong>{aiExplanation.available?"IA local":"Modo sem IA"}</strong>{aiExplanation.model?" · "+aiExplanation.model:""}</p><p>{aiExplanation.summary}</p>{aiExplanation.findings.map((f,i)=><article key={i}><strong>Referência {f.evidence_id}</strong><p>{f.explanation}</p></article>)}{aiExplanation.uncertainties.length>0&&<><h3>Incertezas</h3>{aiExplanation.uncertainties.map((x,i)=><p key={i}>• {x}</p>)}</>}{aiExplanation.warning&&<p className="muted">{aiExplanation.warning}</p>}</div>}</section>}
   {data.role==="instrutor"&&<section className="panel" hidden={activeView!=="planejamento"}><h2>Problemas contextuais</h2><p className="muted">Propostas pedagógicas baseadas nos indicadores da partida, sem geração aleatória ou IA generativa.</p><button onClick={loadContext}>Analisar situação</button>{context&&<div className="timeline">{context.problems.length===0?<p className="muted">Nenhum gatilho contextual ativo neste turno.</p>:context.problems.map(p=><article key={p.id}><b>{p.title}</b><p>{p.summary}</p><p><strong>Gatilho:</strong> {p.trigger}</p><p><strong>Evidências:</strong> {p.evidence.join(" · ")}</p><p>{p.question}</p></article>)}</div>}</section>}
   <div hidden={activeView!=="avaliacao"}><HistoricalLibrary/></div><section className="panel" hidden={activeView!=="avaliacao"}><h2>Biblioteca doutrinária local</h2><p className="muted">Catálogo inicial de metadados. Nenhum manual completo foi importado ou validado.</p><div className="search"><input aria-label="Pesquisar referências" placeholder="Ex.: logística, PPCOT, DAMEPLAN" value={query} onChange={e=>setQuery(e.target.value)}/><button onClick={searchDoctrine}>Pesquisar</button></div>{doctrine&&<div className="timeline">{doctrine.items.length===0?<p className="muted">Nenhuma referência encontrada.</p>:doctrine.items.map(d=><article key={d.code}><b>{d.code}</b> — {d.title}<p>{d.category} · {d.edition_status}</p><p>{d.verification}</p><a href={d.reference_url} target="_blank" rel="noreferrer">Portal institucional</a></article>)}</div>}</section>
   </div></>}
  {error&&<p className="error" role="alert">{error}</p>}<footer>SIMCOTER · Dados, organizações e resultados exclusivamente fictícios · Sem função de comando e controle real</footer>
 </main>
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
