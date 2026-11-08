# Cartografia MapLibre — protótipo 0.7

O desenho SVG anterior foi substituído no frontend React por **MapLibre GL JS**.
O protótipo inclui:

- mapa-base raster OpenStreetMap de visualização **online**;
- controle visível de zoom (+ e −), bússola e escala métrica;
- pan, rolagem e gesto de pinça em dispositivos sensíveis ao toque, conforme navegador;
- marcadores GeoJSON para organizações inteiramente fictícias;
- medidas vetoriais GeoJSON (área e ponto) exibidas após aprovação;
- interação por toque/click em marcador.

### Limites e direitos

A base raster usa os tiles públicos `https://tile.openstreetmap.org/{z}/{x}/{y}.png` apenas para demonstrações de baixo volume e com atribuição. **Não usá-los para baixar mapas em massa nem para pacotes offline.** Em produção, configurar um provedor de mapas com licença e capacidade compatíveis ou hospedar tiles próprios.

O mapa demonstra georreferenciamento e interação, **não é uma carta topográfica militar** e não possui relevo, curvas de nível ou cartas oficiais. A área, os pontos e as organizações são apenas exemplos fictícios colocados sobre coordenadas reais e não indicam localização de unidades ou estruturas militares.

O aplicativo ainda depende de internet para carregar a base OSM. A etapa offline requer tiles autorizados, armazenamento local e política de atualização. A interface em iPad depende de Safari com WebGL ativado.

### Referências

- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [Controles de navegação](https://maplibre.org/maplibre-gl-js/docs/examples/display-map-navigation-controls/)
- [Política de uso de tiles OSM](https://operations.osmfoundation.org/policies/tiles/)
