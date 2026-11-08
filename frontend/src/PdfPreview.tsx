import {useState} from "react";
export default function PdfPreview({sessionId}:{sessionId:string}) {
 const [pages,setPages]=useState<{page:number;text:string}[]>([]),[message,setMessage]=useState(""),[busy,setBusy]=useState(false);
 async function read(file?:File) {
  if(!file)return;
  setPages([]);setMessage("");setBusy(true);
  try {
   if(file.size>2_000_000)throw new Error("PDF excede 2 MB.");
   const response=await fetch("/api/sessions/"+sessionId+"/document-preview",{method:"POST",headers:{"Content-Type":"application/pdf","Authorization":"Bearer "+sessionStorage.getItem("simcoter-token")},body:file});
   const data=await response.json();if(!response.ok)throw new Error(data.detail);
   setPages(data.pages);setMessage(data.warning);
  } catch(e){setMessage(String(e))}finally{setBusy(false)}
 }
 return <section className="panel"><h2>Importar ordem fictícia em PDF</h2>
 <p>Prévia local para conferência. Até 2 MB e 30 páginas com texto selecionável. O arquivo não é salvo nem enviado à IA.</p>
 <label>PDF do exercício<input type="file" accept="application/pdf,.pdf" disabled={busy} onChange={e=>{void read(e.target.files?.[0]);e.target.value=""}}/></label>
 <p role="status">{busy?"Extraindo texto…":message}</p>
 {pages.map(p=><details key={p.page}><summary>Página {p.page}</summary><pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{p.text||"Página sem texto."}</pre></details>)}
 {pages.length>0&&<><p>Confira as páginas e transcreva os trechos relevantes nos campos abaixo. Unidades, apoios e posições precisam de cadastro e aprovação humana.</p><button onClick={()=>{setPages([]);setMessage("")}}>Descartar prévia PDF</button></>}
 </section>
}
