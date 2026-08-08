from pathlib import Path

from .document_factory import LoaderFactory
from .document_loader import DocumentLoaderService
from .document_converter import faq_to_document, ticket_to_document


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "cleaned"


# faq Transform
def faq_transform():
    faq_path = INPUT_DIR / "faq_clean.csv"

    faq_loader = LoaderFactory.create_from_path(faq_path)
    faq_service = DocumentLoaderService(faq_loader)
    faq_rows = faq_service.load_document(faq_path)
    faq_documents = [faq_to_document(row) for row in faq_rows]

    return faq_documents


# tickets Transform
def tickets_transform():
    tickets_path = INPUT_DIR / "tickets_clean.csv"

    tickets_loader = LoaderFactory.create_from_path(tickets_path)
    tickets_service = DocumentLoaderService(tickets_loader)
    tickets_rows = tickets_service.load_document(tickets_path)
    tickets_documents = [ticket_to_document(row) for row in tickets_rows]

    return tickets_documents