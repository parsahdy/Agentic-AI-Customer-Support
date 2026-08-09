from .document_processor import (
    BaseProcessor,
    TextProcessor,
    MetaDataProcessor,
    DuplicationProcessor,
)


class ProcessFactory:

    _processors = {
        "text": TextProcessor,
        "metadata": MetaDataProcessor,
        "duplicate": DuplicationProcessor,
    }

    @classmethod
    def create(cls, processor: str) -> BaseProcessor:

        processor = processor.lower().strip()

        if processor not in cls._process:
            raise ValueError(
                f"Unknown processor: {processor}."
                f"Valid processors: {list(cls._process.keys())}"
            )

        processor_class = cls._process[processor]
        return processor_class()


class ProcessingPipeline:

    def __init__(self, processors: list[BaseProcessor]):
        self.processors = processors

    def run(self, documents: list[dict]) -> list[dict]:

        processed_documents = documents

        for processor in self.processors:
            processed_documents = processor.process(processed_documents)

        return processed_documents


def build_pipeline() -> ProcessingPipeline:

    processors = [
        ProcessFactory.create("text"),
        ProcessFactory.create("metadata"),
        ProcessFactory.create("duplicate"),
    ]

    return ProcessingPipeline(processors)