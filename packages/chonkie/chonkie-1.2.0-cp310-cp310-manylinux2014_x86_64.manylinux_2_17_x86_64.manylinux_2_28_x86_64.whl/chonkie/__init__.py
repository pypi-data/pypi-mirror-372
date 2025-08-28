"""Main package for Chonkie."""

from .chef import (
    BaseChef,
    TextChef,
)
from .chunker import (
    BaseChunker,
    CodeChunker,
    LateChunker,
    NeuralChunker,
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    SlumberChunker,
    TokenChunker,
)
from .cloud import (
    auth,
    chunker,
    refineries,
)
from .embeddings import (
    AutoEmbeddings,
    BaseEmbeddings,
    CohereEmbeddings,
    GeminiEmbeddings,
    JinaEmbeddings,
    Model2VecEmbeddings,
    OpenAIEmbeddings,
    SentenceTransformerEmbeddings,
    VoyageAIEmbeddings,
)
from .fetcher import (
    BaseFetcher,
    FileFetcher,
)
from .friends import (
    BaseHandshake,
    BasePorter,
    ChromaHandshake,
    JSONPorter,
    MongoDBHandshake,
    PgvectorHandshake,
    PineconeHandshake,
    QdrantHandshake,
    TurbopufferHandshake,
    WeaviateHandshake,
)
from .genie import (
    BaseGenie,
    GeminiGenie,
    OpenAIGenie,
)
from .refinery import (
    BaseRefinery,
    EmbeddingsRefinery,
    OverlapRefinery,
)
from .tokenizer import (
    CharacterTokenizer,
    Tokenizer,
    WordTokenizer,
)
from .types import (
    Chunk,
    CodeChunk,
    Context,
    LanguageConfig,
    LateChunk,
    MergeRule,
    RecursiveChunk,
    RecursiveLevel,
    RecursiveRules,
    SemanticChunk,
    SemanticSentence,
    Sentence,
    SentenceChunk,
    SplitRule,
)
from .utils import (
    Hubbie,
    Visualizer,
)

# This hippo grows with every release 🦛✨~
__version__ = "1.2.0"
__name__ = "chonkie"
__author__ = "🦛 Chonkie Inc"


# Add basic package metadata to __all__
__all__ = [
    "__name__",
    "__version__",
    "__author__",
]

# Add all data classes to __all__
__all__ += [
    "Context",
    "Chunk",
    "RecursiveChunk",
    "RecursiveLevel",
    "RecursiveRules",
    "SentenceChunk",
    "SemanticChunk",
    "Sentence",
    "SemanticSentence",
    "LateChunk",
    "CodeChunk",
    "LanguageConfig",
    "MergeRule",
    "SplitRule",
]

# Add all tokenizer classes to __all__
__all__ += [
    "Tokenizer",
    "CharacterTokenizer",
    "WordTokenizer",
]

# Add all chunker classes to __all__
__all__ += [
    "BaseChunker",
    "TokenChunker",
    "SentenceChunker",
    "SemanticChunker",
    "RecursiveChunker",
    "LateChunker",
    "CodeChunker",
    "SlumberChunker",
    "NeuralChunker",
]

# Add all cloud classes to __all__
__all__ += [
    "auth",
    "chunker",
    "refineries",
]

# Add all embeddings classes to __all__
__all__ += [
    "BaseEmbeddings",
    "Model2VecEmbeddings",
    "SentenceTransformerEmbeddings",
    "OpenAIEmbeddings",
    "CohereEmbeddings",
    "GeminiEmbeddings",
    "AutoEmbeddings",
    "JinaEmbeddings",
    "VoyageAIEmbeddings",
]

# Add all refinery classes to __all__
__all__ += [
    "BaseRefinery",
    "OverlapRefinery",
    "EmbeddingsRefinery",
]

# Add all utils classes to __all__
__all__ += [
    "Hubbie",
    "Visualizer",
]

# Add all genie classes to __all__
__all__ += [
    "BaseGenie",
    "GeminiGenie",
    "OpenAIGenie",
]

# Add all friends classes to __all__
__all__ += [
    "BasePorter",
    "BaseHandshake",
    "JSONPorter",
    "ChromaHandshake",
    "MongoDBHandshake",
    "PgvectorHandshake",
    "PineconeHandshake",
    "QdrantHandshake",
    "WeaviateHandshake",
    "TurbopufferHandshake",
]

# Add all the chefs to __all__
__all__ += [
    "BaseChef",
    "TextChef",
]

# Add all the fetchers to __all__
__all__ += [
    "BaseFetcher",
    "FileFetcher",
]
