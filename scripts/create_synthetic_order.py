"""Gera exemplo original. Dependência de autoria opcional: reportlab."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/"frontend/public/examples/ordem-sintetica.pdf"
dest.parent.mkdir(parents=True,exist_ok=True)
styles=getSampleStyleSheet()
styles["Normal"].fontSize=10
styles["Normal"].leading=15
styles["Title"].textColor=colors.HexColor("#254b40")
story=[]
def text(value,style="Normal"):
    story.append(Paragraph(value,styles[style]));story.append(Spacer(1,9))
def footer(canvas,doc):
    canvas.setFont("Helvetica",8)
    canvas.drawString(42,30,"SIMCOTER | Exemplo original inteiramente sintetico | 08/11/2026")
    canvas.drawRightString(550,30,str(doc.page))
text("Ordem de exercício Horizonte","Title")
text("EXEMPLO SINTÉTICO - SEM DADOS OPERACIONAIS REAIS","Heading2")
text("Documento criado do zero para testar importação e revisão no SIMCOTER. Não deriva de ordem real ou classificada, não contém dados DAMEPLAN e não constitui modelo doutrinário homologado.")
text("1. Situação inicial","Heading2")
text("Vale Sereno é uma localidade inventada, representada em um tabuleiro abstrato de 0 a 100. Não corresponde a coordenadas geográficas. As equipes Azul e Vermelha representam papéis de aprendizagem.")
text("2. Objetivo pedagógico","Heading2")
text("Distinguir fatos do cenário, hipóteses e lacunas; conferir a fonte das informações e manter um registro de decisões revisável.")
text("3. Organização fictícia","Heading2")
text("Os agrupamentos abaixo testam categorias de cadastro, sem representar armamento, efetivo ou poder de combate.")
rows=[["Identificador","Nome fictício","Categoria documental","Superior"],
["AZ-COORD","Equipe Aurora","Coordenação","Nenhum"],
["AZ-MAN","Equipe Horizonte","Manobra (rótulo didático)","AZ-COORD"],
["AZ-APOIO","Equipe Cedro","Apoio ao combate (rótulo)","AZ-COORD"],
["AZ-LOG","Equipe Ipê","Apoio logístico (rótulo)","AZ-COORD"]]
table=Table([[Paragraph(v,styles["Normal"]) for v in row] for row in rows],colWidths=[80,110,190,90],repeatRows=1)
table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e2e8df")),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#b2beb0")),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story.append(table);story.append(Spacer(1,14))
text("Posições: não informadas. Disponibilidade: não informada. O importador não deve inventar esses valores nem posicionar elementos automaticamente.")
text("4. Instruções e apoio","Heading2")
text("O instrutor revisa a documentação antes de aprovar o cenário. As equipes registram informações sem formular emprego operacional real. Recursos permanecem abstratos; não há coeficientes de embate ou previsão de perdas.")
story.append(PageBreak())
text("Quadro de informações e conferência","Title")
for title,body in [
("Terreno","Hipótese: a ponte fictícia pode estar indisponível. Fonte: ficha sintética do instrutor. Validade: turno 0. Falta confirmação; não tratar como fato."),
("Condições meteorológicas","Fato do cenário: um novo boletim será entregue no turno 2. Fonte: roteiro sintético. Condições e efeitos ainda não definidos."),
("Adversário fictício","Lacuna conhecida: não há composição ou posição fornecida. Não inferir capacidades nem intenções."),
("Condicionantes civis","Fato do cenário: escola e posto de atendimento inteiramente fictícios aparecem no contexto narrativo. Fonte: roteiro sintético, turno 0. Não são alvos ou coordenadas."),
("5. Coordenação e revisão","Aprovação humana obrigatória. Verificar fonte, validade e classificação das informações. O quadro é documental; não constitui análise PITCIC automatizada."),
("6. Critérios de aceitação da importação","Extrair duas páginas; preservar os nomes e a indicação de incerteza; não cadastrar unidades automaticamente; não substituir hipóteses por fatos; não gravar ou transmitir o PDF a serviços externos."),
("7. DAMEPLAN","Nenhum dado DAMEPLAN foi incorporado. Referências futuras precisam de edição e autorização identificadas. O presente exemplo não permite validar regras de embate."),
("8. Proveniência","Texto e tabela originais produzidos para este projeto em 08/11/2026. Sem reprodução de documentos, mapas ou imagens de terceiros. Não é desclassificação de material existente.")
]:
    text(title,"Heading2");text(body)
SimpleDocTemplate(str(dest),pagesize=(595,842),leftMargin=42,rightMargin=42,topMargin=38,bottomMargin=50,title="SIMCOTER - Ordem sintetica Horizonte",author="SIMCOTER").build(story,onFirstPage=footer,onLaterPages=footer)
print(dest)
