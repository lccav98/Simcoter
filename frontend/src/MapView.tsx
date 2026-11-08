import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import {
  createUnitMarker, symbolMarkup, safeKind, safeEchelon, readinessInfo,
  unitDescription, KIND_LABELS, ECHELON_LABELS, PARTY_LABELS,
  type SimUnit, type Party, type UnitKind,
} from "./militarySymbols";

type Measure = {id:string;name:string;kind:string;status:"proposed"|"approved"};
type Props = {units:SimUnit[];features:Measure[]};
type Filters = {parties:Record<Party,boolean>;kinds:Record<UnitKind,boolean>;overlays:boolean};
const ANCHOR:[number,number]=[-47.9292,-15.7801];
const INITIAL_FILTERS:Filters = {
  parties:{azul:true,vermelha:true},
  kinds:{infantry:true,logistics:true,command:true,engineering:true,communications:true,medical:true,transport:true},
  overlays:true,
};
const unitCoordinates=(unit:SimUnit):[number,number]=>[
  ANCHOR[0]+(unit.x-50)*0.004,ANCHOR[1]-(unit.y-50)*0.004,
];
function overlays(features:Measure[],show:boolean) {
  const area=show&&features.some(f=>f.id==="area-azul"&&f.status==="approved");
  const point=show&&features.some(f=>f.id==="ponto-1"&&f.status==="approved");
  return {
    area:{type:"FeatureCollection" as const,features:area?[{
      type:"Feature" as const,properties:{name:"Área didática fictícia"},
      geometry:{type:"Polygon" as const,coordinates:[[
        [-48.07,-15.68],[-47.98,-15.68],[-47.98,-15.87],[-48.07,-15.87],[-48.07,-15.68],
      ]]},
    }]:[]},
    point:{type:"FeatureCollection" as const,features:point?[{
      type:"Feature" as const,properties:{name:"Ponto administrativo fictício"},
      geometry:{type:"Point" as const,coordinates:[-47.93,-15.83]},
    }]:[]},
  };
}

export default function MapView({units,features}:Props) {
  const container=useRef<HTMLDivElement|null>(null);
  const mapRef=useRef<maplibregl.Map|null>(null);
  const markers=useRef<maplibregl.Marker[]>([]);
  const latest=useRef({units,features,filters:INITIAL_FILTERS});
  const [filters,setFilters]=useState<Filters>(INITIAL_FILTERS);
  const [legendOpen,setLegendOpen]=useState(false);
  const [error,setError]=useState("");
  latest.current={units,features,filters};

  const syncMarkers=(map:maplibregl.Map,items:SimUnit[],f:Filters)=>{
    markers.current.forEach(m=>m.remove());
    markers.current=items
      .filter(u=>Boolean(f.parties[u.party])&&Boolean(f.kinds[safeKind(u.kind)]))
      .map(unit=>new maplibregl.Marker({
        element:createUnitMarker(unit),anchor:"center",
      }).setLngLat(unitCoordinates(unit))
        .setPopup(new maplibregl.Popup({offset:18}).setText(unitDescription(unit)+` · Índice didático: ${readinessInfo(unit).value}% (${readinessInfo(unit).label})`))
        .addTo(map));
  };
  const syncOverlays=(map:maplibregl.Map,items:Measure[],show:boolean)=>{
    const data=overlays(items,show);
    (map.getSource("sim-area") as maplibregl.GeoJSONSource|undefined)?.setData(data.area);
    (map.getSource("sim-point") as maplibregl.GeoJSONSource|undefined)?.setData(data.point);
  };

  useEffect(()=>{
    if(!container.current||mapRef.current)return;
    if(!maplibregl.supported()){
      setError("Este navegador não disponibiliza WebGL para o MapLibre.");
      return;
    }
    const map=new maplibregl.Map({
      container:container.current,
      style:{
        version:8,
        sources:{"osm-base":{type:"raster",
          tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize:256,maxzoom:19,attribution:"© OpenStreetMap contributors"}},
        layers:[{id:"osm-base-layer",type:"raster",source:"osm-base"}],
      },
      center:ANCHOR,zoom:10.2,attributionControl:true,
    });
    mapRef.current=map;
    map.addControl(new maplibregl.NavigationControl({showZoom:true,showCompass:true}),"top-right");
    map.addControl(new maplibregl.ScaleControl({maxWidth:120,unit:"metric"}),"bottom-left");
    // style.load independe do download efetivo dos tiles públicos.
    map.once("style.load",()=>{
      const current=latest.current;
      const data=overlays(current.features,current.filters.overlays);
      map.addSource("sim-area",{type:"geojson",data:data.area});
      map.addLayer({id:"sim-area-fill",type:"fill",source:"sim-area",
        paint:{"fill-color":"#2162b5","fill-opacity":0.12}});
      map.addLayer({id:"sim-area-border",type:"line",source:"sim-area",
        paint:{"line-color":"#2162b5","line-width":2,"line-dasharray":[3,2]}});
      map.addSource("sim-point",{type:"geojson",data:data.point});
      map.addLayer({id:"sim-point-symbol",type:"circle",source:"sim-point",
        paint:{"circle-color":"#eac170","circle-radius":11,
          "circle-stroke-color":"#664719","circle-stroke-width":2}});
      syncMarkers(map,current.units,current.filters);
    });
    map.on("error",()=>setError("Falha ao carregar parte do mapa. Confira a conexão à internet."));
    return ()=>{
      markers.current.forEach(m=>m.remove());
      markers.current=[];
      map.remove();
      mapRef.current=null;
    };
    // O mapa nasce uma única vez; sincronização dos props no efeito seguinte.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);
  useEffect(()=>{
    const map=mapRef.current;
    if(!map||!map.getSource("sim-area"))return;
    syncMarkers(map,units,filters);
    syncOverlays(map,features,filters.overlays);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[units,features,filters]);

  const visibleUnits=units.filter(u=>filters.parties[u.party]&&filters.kinds[safeKind(u.kind)]);
  const representedKinds=Array.from(new Set(units.map(u=>safeKind(u.kind))));
  const setParty=(party:Party,checked:boolean)=>setFilters(f=>({
    ...f,parties:{...f.parties,[party]:checked},
  }));
  const setKind=(kind:UnitKind,checked:boolean)=>setFilters(f=>({
    ...f,kinds:{...f.kinds,[kind]:checked},
  }));
  return <div className="mapShell">
    <div className="mapToolbar">
      <span className="mapToolbarTitle">CARTA INTERATIVA <span>• cenário fictício</span></span>
      <button type="button" className="mapLegendToggle"
        aria-expanded={legendOpen} aria-controls="simcoter-map-legend"
        onClick={()=>setLegendOpen(v=>!v)}>
        {legendOpen?"Ocultar legenda":"Legenda e camadas"}
      </button>
    </div>
    <div className="mapReal" ref={container} role="application"
      aria-label="Mapa geográfico interativo MapLibre GL JS"/>
    {legendOpen&&<section className="mapLegend" id="simcoter-map-legend"
      aria-label="Legenda e filtros cartográficos">
      <div className="legendHeader">
        <strong>Simbologia didática</strong>
        <span>{visibleUnits.length} de {units.length} unidades exibidas</span>
      </div>
      <div className="legendFilters">
        <fieldset>
          <legend>Partidos</legend>
          {(["azul","vermelha"] as const).map(p=><label key={p}>
            <input type="checkbox" checked={filters.parties[p]}
              onChange={e=>setParty(p,e.target.checked)}/>
            {PARTY_LABELS[p]}
          </label>)}
        </fieldset>
        <fieldset>
          <legend>Naturezas cadastradas</legend>
          {representedKinds.map(kind=><label key={kind}>
            <input type="checkbox" checked={filters.kinds[kind]}
              onChange={e=>setKind(kind,e.target.checked)}/>
            {KIND_LABELS[kind]}
          </label>)}
        </fieldset>
        <fieldset>
          <legend>Camadas</legend>
          <label><input type="checkbox" checked={filters.overlays}
            onChange={e=>setFilters(f=>({...f,overlays:e.target.checked}))}/>
            Medidas gráficas aprovadas</label>
        </fieldset>
      </div>
      <div className="symbolLegendList">
        {units.map(unit=><div className="symbolLegendItem" key={unit.id}>
          <span className="symbolLegendIcon" aria-hidden="true"
            dangerouslySetInnerHTML={{__html:symbolMarkup(unit.party,safeKind(unit.kind),safeEchelon(unit.echelon))}}/>
          <span>{unit.name}<small>{KIND_LABELS[safeKind(unit.kind)]} · {ECHELON_LABELS[safeEchelon(unit.echelon)]} · {PARTY_LABELS[unit.party]}</small><small className={"readiness-text "+readinessInfo(unit).status}>Índice didático: {readinessInfo(unit).value}% — {readinessInfo(unit).label}</small></span>
        </div>)}
      </div>
      <p className="legendWarning">Índice sintético de disponibilidade: acima de 50% disponível; de 26% a 50% atenção; 25% ou menos indisponível para ações simuladas. Não é uma medida real de poder de combate.</p><p className="legendWarning">Ícones originais simplificados; não são símbolos militares certificados nem posições reais.</p>
    </section>}
    {error&&<p className="mapError" role="alert">{error}</p>}
    <div className="mapDisclaimer">MapLibre GL JS · Base OSM online · Calcos e organizações inteiramente fictícios · Zoom +/− e pinça no iPad</div>
  </div>;
}
