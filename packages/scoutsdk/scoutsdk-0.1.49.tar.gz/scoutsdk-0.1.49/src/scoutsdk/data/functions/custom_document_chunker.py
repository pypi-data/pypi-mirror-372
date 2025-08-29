from scoutsdk import scout
from scouttypes.document_chunker import (
    DocumentChunks,
    Chunk,
    ChunkMetadata,
    AbstractDocumentChunker,
)


@scout.document_chunker(
    priority=2
)  # Lower priority means that this chunker will be validated first
class DemoChunker(AbstractDocumentChunker):
    def supports_document(
        self, url: str
    ) -> bool:  # Return true when your document chunker
        return False

    def process_document(
        self, url: str
    ) -> DocumentChunks:  # Return the chunks to embed the documents
        return DocumentChunks(
            chunks=[
                Chunk(
                    chunk_to_embed="The content transformed into embeddings",
                    content_to_return="The content returned to the assistant when the embedding match the request.",
                    metadata=ChunkMetadata(
                        hierarchy=["heading 1", "heading 2"],
                        custom_property="Will be returned to the model",
                    ),
                )
            ]
        )
