import { test, expect } from "@playwright/test";
import {
  KIND_LABELS, ECHELON_LABELS, PARTY_LABELS,
  safeKind, safeEchelon, symbolMarkup,
} from "../src/militarySymbols";

test("catálogo mantém naturezas, escalões e partidos tipados", () => {
  expect(Object.keys(KIND_LABELS)).toEqual([
    "infantry", "logistics", "command", "engineering",
    "communications", "medical", "transport",
  ]);
  expect(Object.keys(ECHELON_LABELS)).toEqual([
    "platoon", "company", "battalion", "brigade",
  ]);
  expect(Object.keys(PARTY_LABELS)).toEqual(["azul", "vermelha"]);
});

test("natureza e escalão desconhecidos usam padrão seguro", () => {
  expect(safeKind("inválido")).toBe("infantry");
  expect(safeEchelon("inexistente")).toBe("company");
  expect(safeKind("<script>alert(1)</script>")).toBe("infantry");
});

test("SVG é original e usa somente valores internos do catálogo", () => {
  for(const kind of Object.keys(KIND_LABELS) as (keyof typeof KIND_LABELS)[]){
    for(const party of ["azul","vermelha"] as const){
      const svg=symbolMarkup(party,kind,"battalion");
      expect(svg).toContain("<svg");
      expect(svg).toContain("</svg>");
      expect(svg).toContain('viewBox="0 0 98 82"');
      expect(svg).not.toContain("<script");
      expect(svg).not.toContain("http://www.w3.org/1999/xlink");
    }
  }
});
