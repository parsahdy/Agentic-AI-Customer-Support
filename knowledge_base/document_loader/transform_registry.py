from . import document_transform

TRANSFORMS = {
    "faq": document_transform.faq_transform,
    "ticket": document_transform.tickets_transform,
    "pdf": document_transform.pdf_transform,
}