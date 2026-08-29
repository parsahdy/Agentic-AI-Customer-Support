from knowledge_base.document_loader.document_transform import faq_transform
from knowledge_base.document_processor.processing_pipeline import build_pipeline


def document_processing():

    documents = faq_transform()

    pipeline = build_pipeline()

    processed_documents = pipeline.run(documents)

    return processed_documents
 

if __name__ == "__main__":
    print(document_processing())
