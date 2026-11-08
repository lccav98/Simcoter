# Prévia documental de PDF
Em Planejamento, "Importar ordem fictícia em PDF" recebe PDF de até 2 MB e 30 páginas com texto selecionável. A extração local ocorre em processo separado com timeout de 10 s e limite de 60.000 caracteres. Documentos protegidos, inválidos ou sem texto são recusados. OCR não implementado. O timeout não é isolamento de memória do sistema operacional.

A autenticação de instrutor ocorre antes da leitura. O PDF não é gravado no banco nem enviado à IA. Prévia por página serve para conferência e transcrição manual; tabelas, colunas e diagramas podem perder a ordem visual. Texto não é executado ou interpretado como instrução.

Esta entrega NÃO reconhece automaticamente elementos de manobra/apoio, não georreferencia símbolos e não calcula embates pelo DAMEPLAN. Meios e posições continuam cadastrados manualmente e aprovados na preparação. Integração documental futura exige amostra fictícia representativa e identificação da edição e direitos de uso da referência. Parâmetros operacionais reais permanecem fora do escopo autorizado.

Validação: build aprovado e 57 testes Python passaram, incluindo extração de texto real em PDF sintético, rejeição de arquivos, autorização e preservação da partida. Avisos conhecidos: Starlette/httpx e tamanho do bundle.
