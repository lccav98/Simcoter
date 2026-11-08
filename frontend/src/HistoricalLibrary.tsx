export const historicalCases = [
 {title:"Monte Castelo",date:"21 de fevereiro de 1945",publisher:"Ministério da Defesa",
 url:"https://www.gov.br/defesa/pt-br/acesso-a-informacao/institucional-2/ministro-da-defesa/jose-mucio-monteiro-filho/arquivos/03-tomada-de-monte-castelo-78-anos.pdf",
 summary:"A participação brasileira na campanha da Itália inclui a conquista de Monte Castelo pela FEB em fevereiro de 1945.",
 question:"Quais afirmações são documentadas e quais condições ambientais ainda precisam de fontes independentes?"},
 {title:"Waterloo",date:"18 de junho de 1815",publisher:"National Army Museum",
 url:"https://www.nam.ac.uk/explore/battle-waterloo",
 summary:"O confronto reuniu o exército francês de Napoleão e a coalizão associada a Wellington e Blücher, marcando o encerramento do poder imperial napoleônico.",
 question:"Como distinguir o conhecimento disponível aos participantes da interpretação posterior dos historiadores?"},
 {title:"Batalha da Grã-Bretanha",date:"10 de julho a 31 de outubro de 1940",publisher:"RAF Museum",
 url:"https://www.rafmuseum.org.uk/research/online-exhibitions/history-of-the-battle-of-britain/introduction-to-the-phases-of-the-battle-of-britain/",
 summary:"A periodização britânica apresentada pelo museu situa a batalha aérea entre julho e outubro de 1940.",
 question:"Como registrar mudanças temporais, incerteza das informações e consequências civis sem reduzir o estudo a um resultado militar?"},
];
export default function HistoricalLibrary() {
 return <section className="panel"><h2>Casos históricos para estudo</h2>
 <p>Resumos originais e referências institucionais consultadas em 08/11/2026. Documentos, imagens e mapas das fontes não foram incorporados; direitos de reprodução não verificados.</p>
 {historicalCases.map(c=><article key={c.title}><h3>{c.title}</h3><p>{c.date} · {c.publisher}</p><p>{c.summary}</p>
 <a href={c.url} target="_blank" rel="noreferrer">Consultar fonte de {c.title}</a><p>Questão de estudo: {c.question}</p></article>)}
 <p>Para um exercício inspirado nesses temas, registre hipóteses e fontes em Planejamento e use somente meios e parâmetros fictícios. Estes registros não são reconstruções históricas executáveis; não há calibração de combate real.</p></section>
}
