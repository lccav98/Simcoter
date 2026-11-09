import {useState} from "react";
export default function TurnCycle({id,turn,orders,onChange}:{id:string;turn:number;orders:{unit_id:string;x:number;y:number}[];onChange:(state:any)=>void}){
 const [review,setReview]=useState<any>(null),[error,setError]=useState(""),[busy,setBusy]=useState(false);
 async function request(path:string,body?:unknown){
  const r=await fetch("/api/sessions/"+id+path,{method:body===undefined?"GET":"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+sessionStorage.getItem("simcoter-token")},body:body===undefined?undefined:JSON.stringify(body)});
  const result=await r.json();if(!r.ok)throw new Error(result.detail);return result;
 }
 async function act(action:string){setBusy(true);setError("");try{
  if(action==="review")setReview(await request("/turn-review"));
  else {onChange(await request(action==="clear"?"/clear-orders":"/turns",action==="clear"?{}:{token:review?.token}));setReview(null)}
 }catch(e){setError(String(e));setReview(null)}finally{setBusy(false)}}
 return <section className="panel"><h2>Ciclo do turno</h2><p>Preparar → registrar ordens → revisar → executar → avaliar. Sem ordens, as posições são mantidas.</p>
 <p>{orders.length} ordens na fila · turno atual {turn}/20</p>{orders.map(o=><p key={o.unit_id}>{o.unit_id}: destino fictício ({o.x}, {o.y})</p>)}
 <button disabled={busy||turn>=20} onClick={()=>void act("review")}>Revisar próximo turno</button>
 <button disabled={busy||!orders.length} onClick={()=>void act("clear")}>Limpar ordens do turno</button>
 {review&&<div><h3>Prévia do turno {review.turn}</h3>{review.issues.map((x:string)=><p key={x} role="alert">{x}</p>)}
 <p>{review.warning}</p><p>Evento previsto: {review.event.name??"Turno rotineiro"}</p>
 <table><thead><tr><th>Indicador</th><th>Antes</th><th>Depois</th></tr></thead><tbody>{Object.keys(review.resources_before).map(k=><tr key={k}><td>{k}</td><td>{review.resources_before[k]}</td><td>{review.resources_after[k]}</td></tr>)}</tbody></table>
 {review.orders.map((o:any)=><p key={o.name}>{o.name}: {o.allowed?"Destino permitido":"Bloqueado"}</p>)}
 <button disabled={busy||review.issues.length>0||turn>=20} onClick={()=>void act("execute")}>Avançar turno</button>
 <p>Alterações posteriores exigem nova revisão.</p></div>}{error&&<p role="alert">{error}</p>}</section>
}
