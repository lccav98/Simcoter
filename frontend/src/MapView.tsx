import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

type Unit = {id:string;party:"azul"|"vermelha";name:string;x:number;y:number};
type Measure = {id:string;name:string;kind:string;status:"proposed"|"approved"};
type Props = {units:Unit[];features:Measure[]};

/** Mapa geográfico REAL. As coordenadas de marcadores são exemplos inventados,
 * sem vínculo com o terreno ou com posições de organizações reais.
 * O mapa-base de demonstração é ONLINE e NÃO pode ser baixado em massa.
 */
const ANCHOR: [number, number] = [-47.9292, -15.7801];

const geometry = (units: Unit[], features: Measure[]) => {
  const showArea = features.some(f=>f.id==="area-azul" && f.status==="approved");
  const showPoint = features.some(f=>f.id==="ponto-1" && f.status==="approved");
  return {
    units: {
      type: "FeatureCollection" as const,
      features: units.map((u) => ({
        type: "Feature" as const,
        properties: {id:u.id, party:u.party, name:u.name},
        geometry: {type:"Point" as const, coordinates: [
          ANCHOR[0] + (u.x-50)*0.004,
          ANCHOR[1] - (u.y-50)*0.004,
        ]},
      })),
    },
    area: {
      type:"FeatureCollection" as const,
      features: showArea ? [{
        type:"Feature" as const,
        properties: {name:"Área didática — aprovada"},
        geometry: {type:"Polygon" as const, coordinates:[[
          [-48.07,-15.68],[-47.98,-15.68],[-47.98,-15.87],[-48.07,-15.87],[-48.07,-15.68]
        ]]},
      }] : [],
    },
    point: {
      type:"FeatureCollection" as const,
      features: showPoint ? [{
        type:"Feature" as const, properties:{name:"Ponto administrativo fictício"},
        geometry:{type:"Point" as const,coordinates:[-47.93,-15.83]},
      }] : [],
    },
  };
};

export default function MapView({units,features}:Props) {
  const root = useRef<HTMLDivElement|null>(null);
  const mapRef = useRef<maplibregl.Map|null>(null);
  const dataRef=useRef({units,features});
  dataRef.current={units,features};
  const [error,setError] = useState("");
  useEffect(()=>{
    if (!root.current || mapRef.current) return;
    if (!maplibregl.supported()) {
      setError("Este navegador não disponibiliza WebGL para o MapLibre.");
      return;
    }
    const map = new maplibregl.Map({
      container:root.current,
      style:{
        version:8,
        sources:{
          "osm-base":{type:"raster",tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize:256,maxzoom:19,attribution:"© OpenStreetMap contributors"},
        },
        layers:[{id:"osm-base-layer",type:"raster",source:"osm-base"}],
      },
      center:ANCHOR, zoom:10.2, attributionControl:true,
    });
    mapRef.current=map;
    map.addControl(new maplibregl.NavigationControl({showZoom:true,showCompass:true}),"top-right");
    map.addControl(new maplibregl.ScaleControl({maxWidth:120,unit:"metric"}),"bottom-left");
    map.on("load",()=>{
      const d=geometry(dataRef.current.units,dataRef.current.features);
      map.addSource("sim-units",{type:"geojson",data:d.units});
      map.addLayer({id:"sim-units-circles",type:"circle",source:"sim-units",
        paint:{"circle-radius":10,"circle-color":["case",["==",["get","party"],"azul"],"#2162b5","#b24c4c"],
          "circle-stroke-color":"#fff","circle-stroke-width":2}});
      map.addLayer({id:"sim-units-labels",type:"symbol",source:"sim-units",
        layout:{"text-field":["get","name"],"text-size":12,"text-offset":[0,1.8]},
        paint:{"text-halo-color":"#fff","text-halo-width":2}});
      map.addSource("sim-area",{type:"geojson",data:d.area});
      map.addLayer({id:"sim-area-fill",type:"fill",source:"sim-area",
        paint:{"fill-color":"#2162b5","fill-opacity":0.12}});
      map.addLayer({id:"sim-area-border",type:"line",source:"sim-area",
        paint:{"line-color":"#2162b5","line-width":2,"line-dasharray":[3,2]}});
      map.addSource("sim-point",{type:"geojson",data:d.point});
      map.addLayer({id:"sim-point-symbol",type:"circle",source:"sim-point",
        paint:{"circle-color":"#eac170","circle-radius":11,"circle-stroke-color":"#664719","circle-stroke-width":2}});
      map.on("click","sim-units-circles",(event)=>{
        const f=event.features?.[0];
        if(f?.geometry.type!=="Point") return;
        new maplibregl.Popup().setLngLat(event.lngLat)
          .setText(String(f.properties?.name??"Organização fictícia")).addTo(map);
      });
    });
    map.on("error",()=>setError("Falha ao carregar parte do mapa. Verifique a conexão à internet."));
    return ()=>{map.remove();mapRef.current=null};
    // Criação única. Mudanças nas entidades serão aplicadas pelo efeito abaixo.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);
  useEffect(()=>{
    const map=mapRef.current;
    if(!map || !map.isStyleLoaded()) return;
    const d=geometry(units,features);
    (map.getSource("sim-units") as maplibregl.GeoJSONSource|undefined)?.setData(d.units);
    (map.getSource("sim-area") as maplibregl.GeoJSONSource|undefined)?.setData(d.area);
    (map.getSource("sim-point") as maplibregl.GeoJSONSource|undefined)?.setData(d.point);
  },[units,features]);
  return <div className="mapShell">
    <div className="mapReal" ref={root} role="application" aria-label="Mapa geográfico interativo MapLibre GL JS"/>
    {error&&<p role="alert">{error}</p>}
    <div className="mapDisclaimer">MapLibre GL JS · Base OSM online · Calcos e organizações fictícios, não representam posições reais</div>
  </div>;
}
