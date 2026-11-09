import {useState} from "react";
export type ImportField="objective"|"situation"|"instructions"|"constraints"|"support"|"coordination";
export default function PdfPreview({sessionId,locked=false,onTransfer}:{sessionId:string;locked?:boolean;onTransfer?:(field:ImportField,text:string)=>string|undefined}) {
 const [pages,setPages]=useState<{page:number;text:string}[]>([]),[message,setMessage]=useState(""),[busy,setBusy]=useState(false);
 const [excerpt,setExcerpt]=useState(""),[pageNumber,setPageNumber]=useState(1),[target,setTarget]=useState<ImportField>("situation");
 async function read(file?:File) {
  if(!file)return;
  setPages([]);setExcerpt("");setMessage("");setBusy(true);
  try {
   if(file.size>2_000_000)throw new Error("PDF excede 2 MB.");
   const response=await fetch("/api/sessions/"+sessionId+"/document-preview",{method:"POST",headers:{"Content-Type":"application/pdf","Authorization":"Bearer "+sessionStorage.getItem("simcoter-token")},body:file});
   const data=await response.json();if(!response.ok)throw new Error(data.detail);
   setPages(data.pages);setPageNumber(1);setMessage(data.warning);
  } catch(e){setMessage(String(e))}finally{setBusy(false)}
 }
 async function example() {
  try {
   const response=await fetch("/examples/ordem-sintetica.pdf");
   if(!response.ok)throw new Error("Exemplo indisponível. Recompile a interface.");
   await read(new File([await response.blob()],"ordem-sintetica.pdf",{type:"application/pdf"}));
  } catch(e) {setMessage(String(e))}
 }
 return <section className="panel"><h2>Importar ordem fictícia em PDF</h2>
 <p>Prévia local para conferência. Até 2 MB e 30 páginas com texto selecionável. O arquivo não é salvo nem enviado à IA.</p>
 <p><strong>Não importe material classificado.</strong> O protótipo não foi homologado para tratar documentos sigilosos.</p>
 <button disabled={busy} onClick={()=>void example()}>Carregar exemplo sintético</button>
 <a href="/examples/ordem-sintetica.pdf" download>Baixar PDF de exemplo</a>
 <label>PDF do exercício<input type="file" accept="application/pdf,.pdf" disabled={busy} onChange={e=>{void read(e.target.files?.[0]);e.target.value=""}}/></label>
 <p role="status">{busy?"Extraindo texto…":message}</p>
 {pages.map(p=><details key={p.page}><summary>Página {p.page}</summary><button disabled={locked} onClick={()=>{setExcerpt(p.text);setPageNumber(p.page);setMessage("Revise o trecho antes de transferir. Limite de 2.500 caracteres.");}}>Revisar trecho da página {p.page}</button><pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{p.text||"Página sem texto."}</pre></details>)}
 {pages.length>0&&<>{onTransfer&&<fieldset disabled={locked||busy}><legend>Trecho para o rascunho</legend>
 <label>Trecho revisado<textarea aria-label="Trecho revisado" value={excerpt} onChange={e=>setExcerpt(e.target.value)}/></label>
 <p>{excerpt.length}/2500 caracteres · referência: página {pageNumber}</p>
 <label>Campo de destino<select value={target} onChange={e=>setTarget(e.target.value as ImportField)}>
 {([["objective","Objetivo pedagógico"],["situation","Situação inicial fictícia"],["instructions","Instruções do exercício"],["constraints","Premissas e restrições"],["support","Apoio e recursos abstratos"],["coordination","Coordenação e responsabilidades"]]).map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></label>
 <button disabled={!excerpt.trim()||excerpt.length>2500} onClick={()=>{const error=onTransfer(target,"[PDF revisado, página "+pageNumber+"]\n"+excerpt.trim());setMessage(error??"Trecho acrescentado ao rascunho. Clique em Salvar rascunho para persistir.");if(!error)setExcerpt("");}}>Acrescentar ao rascunho</button>
 </fieldset>}<p>Confira as páginas e transfira apenas trechos revisados. O conteúdo existente é preservado. Unidades, apoios e posições precisam de cadastro e aprovação humana.</p><button onClick={()=>{setPages([]);setMessage("")}}>Descartar prévia PDF</button></>}
 </section>
}
