from typing import Dict, List, Any


class EmbeddingDetector:
    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        exemplars: Dict[str, List[str]] = None,
    ):
        from sentence_transformers import SentenceTransformer, util

        self.model = SentenceTransformer(model_name)
        self.util = util
        self.exemplars = exemplars or {}

        # Pre-encode exemplars for efficiency
        self.exemplar_embeddings = {
            category: self.model.encode(examples, convert_to_tensor=True)
            for category, examples in self.exemplars.items()
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        text_embedding = self.model.encode(text, convert_to_tensor=True)
        scores = {}

        for category, embeddings in self.exemplar_embeddings.items():
            if len(embeddings) > 0:
                similarity = float(
                    self.util.cos_sim(text_embedding, embeddings).max().cpu()
                )
            else:
                similarity = 0.0

            scores[category] = {"similarity": similarity}

        return scores
