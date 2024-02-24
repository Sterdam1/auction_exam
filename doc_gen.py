from docxtpl import DocxTemplate
from datetime import datetime

def gen_default_doc(name, date):
    doc = DocxTemplate(r"doc_templates\default_template.docx")
    context = {'name': name,
               'date': date,}
    doc.render(context)
    filepath = r"docs\generated_doc_"+date.strftime("%d-%m-%Y")+".docx"
    doc.save(filepath)

    return filepath
