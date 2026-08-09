from pathlib import Path

from .document_factory import LoaderFactory
from .document_converter import faq_to_document, ticket_to_document


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "cleaned"
PDF_DIR = PROJECT_ROOT / "data" / "pdf"


# faq Transform
def faq_transform():
    faq_path = INPUT_DIR / "faq_clean.csv"

    faq_loader = LoaderFactory.create_from_path(faq_path)
    faq_rows = faq_loader.load(faq_path)
    faq_documents = [faq_to_document(row) for row in faq_rows]

    return faq_documents


# tickets Transform
def tickets_transform():
    tickets_path = INPUT_DIR / "tickets_clean.csv"

    tickets_loader = LoaderFactory.create_from_path(tickets_path)
    tickets_rows = tickets_loader.load(tickets_path)
    tickets_documents = [ticket_to_document(row) for row in tickets_rows]

    return tickets_documents


def pdf_transform():
    pdf_path = PDF_DIR 

    pdf_loader = LoaderFactory.create("pdf")
    pdf_documents = pdf_loader.load(pdf_path)

    return pdf_documents

