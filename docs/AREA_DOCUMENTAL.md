# Área extraída da documentação — primeira etapa

Em Planejamento, carregue um PDF não classificado com texto selecionável. A extração existente fornece páginas; o novo reconhecedor procura uma declaração explícita por linha:

`AREA_EXERCICIO_WGS84: -48.10,-15.95,-47.80,-15.60`

Os números exemplificam um retângulo de teste, sem relação operacional: oeste, sul, leste, norte em graus decimais WGS84, separados por vírgula, ponto decimal, negativos para oeste/sul. Latitude aceita entre −85 e 85; retângulos cruzando o antimeridiano não são aceitos.

O painel apresenta cada referência com página e texto. Confirme a desejada: o limite é salvo na partida e desenhado em laranja, e o mapa se enquadra nele. Há confirmação humana antes da aplicação; a proposta sozinha não muda a partida. Somente instrutor pode propor/confirmar. A confirmação fica bloqueada após o turno zero. A área documental não é exposta aos tokens de partido.

Não há envio a geocodificadores externos. O PDF inteiro não é persistido por essa função; a confirmação salva os limites, o número da página e a linha selecionada no estado e no histórico. A referência é declarativa, não uma assinatura de autenticidade do PDF.

Limites: não interpreta livremente nomes de cidades, coordenadas UTM/DMS, mapas em imagem ou documentos digitalizados sem OCR. O PDF de exemplo anterior não contém a declaração e portanto apresenta ausência de área reconhecida. A base cartográfica disponível não é ampliada pelo enquadramento: sem mapa licenciado para a região, pode haver apenas fundo e limite. As unidades e zonas do tabuleiro mantêm suas posições abstratas originais; não são automaticamente georreferenciadas ou transferidas para a área documental. Essa etapa seleciona o enquadramento, não integra terreno ao motor.
