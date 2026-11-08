/** SIMCOTER — áudio sintético original gerado localmente por Web Audio API.
 * Não há arquivos de áudio, downloads, serviços externos ou efeitos militares reais.
 * Efeitos são sugestões narrativas para situações FICTÍCIAS, nunca dados da simulação.
 */
export type Cue="routine"|"incident"|"engagement_preview";
export const CUE_LABELS:Record<Cue,string>={
  routine:"Turno rotineiro",
  incident:"Ocorrência do cenário fictício",
  engagement_preview:"Prévia sonora de embate fictício (não é evento da partida)",
};

export class GameAudio {
  private context:AudioContext|null=null;
  private master:GainNode|null=null;
  private enabled=false;
  private volume=0.28;
  private readonly limit=0.45;

  get supported():boolean {
    return typeof AudioContext!=="undefined";
  }

  configure(enabled:boolean,volume:number):void {
    this.enabled=enabled;
    this.volume=Number.isFinite(volume)?Math.min(this.limit,Math.max(0,volume)):0;
    if(this.master) this.master.gain.value=this.enabled?this.volume:0;
  }

  /** Invocar diretamente no botão do usuário: Safari exige gesto para ativar áudio. */
  async unlock():Promise<boolean> {
    if(!this.enabled||!this.supported) return false;
    try {
      if(!this.context||this.context.state==="closed") {
        this.context=new AudioContext();
        this.master=this.context.createGain();
        this.master.gain.value=this.volume;
        this.master.connect(this.context.destination);
      }
      if(this.context.state==="suspended") await this.context.resume();
      return this.context.state==="running";
    } catch {
      return false;
    }
  }

  private tone(
    frequency:number, start:number, duration:number,
    type:OscillatorType="sine", amplitude=0.12, endFrequency?:number,
  ):void {
    if(!this.context||!this.master||this.context.state!=="running") return;
    const osc=this.context.createOscillator();
    const envelope=this.context.createGain();
    osc.type=type;
    osc.frequency.setValueAtTime(Math.max(30,frequency),start);
    if(endFrequency)osc.frequency.exponentialRampToValueAtTime(Math.max(30,endFrequency),start+duration);
    envelope.gain.setValueAtTime(0.0001,start);
    envelope.gain.exponentialRampToValueAtTime(Math.max(0.0002,amplitude),start+0.015);
    envelope.gain.exponentialRampToValueAtTime(0.0001,start+duration);
    osc.connect(envelope).connect(this.master);
    osc.start(start);
    osc.stop(start+duration+0.03);
    osc.onended=()=>{osc.disconnect();envelope.disconnect()};
  }

  /** Ruído limitado e filtrado para uma textura cinematográfica abstrata. */
  private swell(start:number,duration:number):void {
    if(!this.context||!this.master||this.context.state!=="running")return;
    const ctx=this.context;
    const frames=Math.ceil(ctx.sampleRate*duration);
    const buffer=ctx.createBuffer(1,frames,ctx.sampleRate);
    const data=buffer.getChannelData(0);
    // Aleatoriedade usada só para áudio, jamais para o resultado de um turno.
    for(let i=0;i<frames;i++)data[i]=Math.random()*2-1;
    const source=ctx.createBufferSource();
    source.buffer=buffer;
    const filter=ctx.createBiquadFilter();
    filter.type="lowpass";
    filter.frequency.value=380;
    const gain=ctx.createGain();
    gain.gain.setValueAtTime(0.0001,start);
    gain.gain.exponentialRampToValueAtTime(0.045,start+0.035);
    gain.gain.exponentialRampToValueAtTime(0.0001,start+duration);
    source.connect(filter).connect(gain).connect(this.master);
    source.start(start);
    source.stop(start+duration);
    source.onended=()=>{source.disconnect();filter.disconnect();gain.disconnect()};
  }

  play(cue:Cue):boolean {
    if(!this.enabled||!this.context||this.context.state!=="running")return false;
    const t=this.context.currentTime+0.025;
    if(cue==="routine"){
      this.tone(440,t,0.12,"sine",0.12);
      this.tone(587.33,t+0.15,0.15,"sine",0.09);
    }else if(cue==="incident"){
      this.tone(330,t,0.20,"triangle",0.1,245);
      this.tone(220,t+0.19,0.32,"sine",0.10,165);
    }else{
      // Efeito abstrato e curto, sem balística, explosões ou localização espacial.
      this.swell(t,0.52);
      this.tone(128,t,0.42,"triangle",0.14,68);
      this.tone(168,t+0.34,0.45,"sine",0.1,88);
      this.tone(440,t+0.84,0.14,"sine",0.1);
    }
    return true;
  }

  async close():Promise<void> {
    this.enabled=false;
    this.master?.disconnect();
    this.master=null;
    const context=this.context;
    this.context=null;
    if(context&&context.state!=="closed")await context.close().catch(()=>undefined);
  }
}
