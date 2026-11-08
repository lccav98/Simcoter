import type { StyleSpecification } from "maplibre-gl";

// Geometria original e abstrata; não representa feições do terreno real.
// Sem tiles, fontes, sprites ou serviços externos.
export function offlineStyle(): StyleSpecification {
  const lines = Array.from({ length: 11 }, (_, i) => {
    const offset = i * 0.04;
    return [
      { type: "Feature" as const, properties: {}, geometry: {
        type: "LineString" as const, coordinates: [[-48.13 + offset, -15.98], [-48.13 + offset, -15.58]],
      }},
      { type: "Feature" as const, properties: {}, geometry: {
        type: "LineString" as const, coordinates: [[-48.13, -15.98 + offset], [-47.73, -15.98 + offset]],
      }},
    ];
  }).flat();
  return {
    version: 8,
    sources: {
      grid: { type: "geojson", data: { type: "FeatureCollection", features: lines },
        attribution: "SIMCOTER · base sintética original · sem correspondência com terreno real" },
    },
    layers: [
      { id: "offline-background", type: "background", paint: { "background-color": "#e7e5d8" } },
      { id: "offline-grid", type: "line", source: "grid",
        paint: { "line-color": "#a4ab9d", "line-width": 1, "line-opacity": 0.55 } },
    ],
  };
}
