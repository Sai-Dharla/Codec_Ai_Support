import app.compat  # Global import from app.compat
import logging
from typing import List
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

class SemanticModel:
    """
    Hugging Face Transformers semantic embedding engine.
    Computes dense embeddings using Hugging Face AutoModel and AutoTokenizer
    (sentence-transformers/all-MiniLM-L6-v2) with mean pooling and L2 normalization.
    """
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading Hugging Face model & tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
            logger.info("Hugging Face model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Transformers model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load Transformer model '{self.model_name}': {e}")

    def encode(self, texts: List[str]) -> np.ndarray:
        """Generates normalized dense embeddings for input texts."""
        if not texts:
            return np.empty((0, 384))

        with torch.no_grad():
            encoded_input = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors='pt'
            )
            model_output = self.model(**encoded_input)
            
            # Mean Pooling - Take attention mask into account for correct averaging
            token_embeddings = model_output[0]
            input_mask_expanded = encoded_input['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            pooled = sum_embeddings / sum_mask
            
            # Normalize embeddings (L2 normalization)
            normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
            return normalized.cpu().numpy()

    def compute_similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """Calculates cosine similarities between query and knowledge base embeddings."""
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        similarities = np.dot(doc_embeddings, query_embedding.T).flatten()
        return similarities

