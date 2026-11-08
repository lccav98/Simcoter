import io
import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
from backend.app.pdf_import import extract_pdf
from tests.test_api import setup_session

def pdf():
    writer=PdfWriter()
    page=writer.add_blank_page(300,300)
    font=DictionaryObject({NameObject("/Type"):NameObject("/Font"),NameObject("/Subtype"):NameObject("/Type1"),NameObject("/BaseFont"):NameObject("/Helvetica")})
    page[NameObject("/Resources")]=DictionaryObject({NameObject("/Font"):DictionaryObject({NameObject("/F1"):writer._add_object(font)})})
    stream=DecodedStreamObject();stream.set_data(b"BT /F1 12 Tf 30 200 Td (Exercicio ficticio Aurora) Tj ET")
    page[NameObject("/Contents")]=writer._add_object(stream)
    buf=io.BytesIO();writer.write(buf);return buf.getvalue()

def test_real_text_extraction_and_rejection():
    assert "Aurora" in extract_pdf(pdf())["pages"][0]["text"]
    for bad in (b"not pdf",b"%PDF-"+b"x"*2_000_000,b"%PDF-corrupted"):
        with pytest.raises(ValueError): extract_pdf(bad)

def test_pdf_preview_auth_and_no_mutation(tmp_path,monkeypatch):
    client,sid,headers=setup_session(tmp_path,monkeypatch)
    url=f"/api/sessions/{sid}/document-preview"
    before=client.get(f"/api/sessions/{sid}",headers=headers["instrutor"]).json()
    assert client.post(url,content=pdf(),headers=headers["azul"]).status_code==403
    assert client.post(url,content=pdf()).status_code==401
    result=client.post(url,content=pdf(),headers=headers["instrutor"])
    assert result.status_code==200
    assert result.json()["pages"][0]["page"]==1
    assert client.get(f"/api/sessions/{sid}",headers=headers["instrutor"]).json()==before
