import type { FeatureCollection, Feature, LineString } from "geojson";

export type LocalPack = {
  title: string; source: string; license: string; attribution: string;
  data: FeatureCollection<LineString>;
};
export const MAX_PACK_BYTES = 1_000_000;
export function parseLocalPack(text: string): LocalPack {
  if (new TextEncoder().encode(text).length > MAX_PACK_BYTES) throw new Error("Arquivo excede 1 MB.");
  const value = JSON.parse(text);
  if (!value || value.version !== 1 || value.fictional !== true || value.offlineAllowed !== true)
    throw new Error("Declare versão 1, conteúdo fictício e autorização offline.");
  const metadata: Record<string, string> = {};
  for (const key of ["title", "source", "license", "attribution"]) {
    if (typeof value[key] !== "string" || !value[key].trim() || value[key].length > 300)
      throw new Error("Informe título, origem, licença e atribuição (até 300 caracteres).");
    metadata[key] = value[key].trim();
  }
  if (value.data?.type !== "FeatureCollection" || !Array.isArray(value.data.features) ||
      value.data.features.length < 1 || value.data.features.length > 500)
    throw new Error("O pacote deve conter de 1 a 500 linhas GeoJSON.");
  let count = 0;
  const features: Feature<LineString>[] = value.data.features.map((feature: any) => {
    const points = feature?.geometry?.coordinates;
    if (feature?.type !== "Feature" || feature.geometry?.type !== "LineString" ||
        !Array.isArray(points) || points.length < 2)
      throw new Error("Somente linhas vetoriais são aceitas nesta versão.");
    const coordinates = points.map((point: any) => {
      if (++count > 10000 || !Array.isArray(point) || point.length !== 2 ||
          !point.every((n: unknown) => typeof n === "number" && Number.isFinite(n)) ||
          Math.abs(point[0]) > 180 || Math.abs(point[1]) > 85)
        throw new Error("Coordenadas inválidas ou limite de 10.000 pontos excedido.");
      return [point[0], point[1]];
    });
    // Não repassa propriedades, HTML, URLs, estilos ou identificadores do arquivo.
    return { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates } };
  });
  return { ...metadata, data: { type: "FeatureCollection", features } } as LocalPack;
}
