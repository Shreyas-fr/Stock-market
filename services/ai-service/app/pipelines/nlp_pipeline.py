from typing import List, Dict, Optional
from loguru import logger


class NLPPipeline:
    """NLP pipeline: sentiment, NER, classification."""
    
    _sentiment_pipeline = None
    _ner_pipeline = None
    _initialized = False

    @classmethod
    def initialize(cls):
        """Lazy initialization of models."""
        if cls._initialized:
            return
        
        try:
            from transformers import pipeline
            # FinBERT for financial sentiment
            logger.info("Loading FinBERT sentiment model...")
            cls._sentiment_pipeline = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                return_all_scores=True,
                truncation=True,
                max_length=512,
            )
            logger.info("FinBERT loaded")
        except Exception as e:
            logger.warning(f"FinBERT load failed, using fallback: {e}")
            cls._sentiment_pipeline = None
        
        try:
            import spacy
            logger.info("Loading spaCy NER model...")
            cls._ner_pipeline = spacy.load("en_core_web_sm")
            logger.info("spaCy NER loaded")
        except Exception as e:
            logger.warning(f"spaCy load failed: {e}")
            cls._ner_pipeline = None
        
        cls._initialized = True

    @classmethod
    def sentiment(cls, text: str) -> Dict:
        """Analyze financial sentiment of text."""
        if not cls._initialized:
            cls.initialize()
        
        if cls._sentiment_pipeline:
            try:
                results = cls._sentiment_pipeline(text[:512])
                scores = {r["label"]: r["score"] for r in results[0]}
                dominant = max(scores, key=scores.get)
                # Map to -1 to +1 scale
                score = scores.get("positive", 0) - scores.get("negative", 0)
                return {
                    "sentiment": dominant,
                    "score": round(score, 4),
                    "scores": scores,
                }
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Fallback: simple keyword-based
        return cls._keyword_sentiment(text)

    @classmethod
    def _keyword_sentiment(cls, text: str) -> Dict:
        """Simple keyword-based sentiment fallback."""
        positive_words = [
            "growth", "profit", "gain", "rise", "surge", "boost", "improvement",
            "strong", "record", "beat", "exceed", "opportunity", "bullish", "expand",
        ]
        negative_words = [
            "loss", "decline", "fall", "risk", "shortage", "disruption", "tariff",
            "sanction", "ban", "cut", "weak", "miss", "bearish", "crisis", "debt",
        ]
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            sentiment, score = "positive", min(0.5 + (pos_count - neg_count) * 0.1, 1.0)
        elif neg_count > pos_count:
            sentiment, score = "negative", max(-0.5 - (neg_count - pos_count) * 0.1, -1.0)
        else:
            sentiment, score = "neutral", 0.0
        
        return {"sentiment": sentiment, "score": round(score, 4), "method": "keyword"}

    @classmethod
    def extract_entities(cls, text: str) -> List[Dict]:
        """Extract named entities from text."""
        if not cls._initialized:
            cls.initialize()
        
        if cls._ner_pipeline:
            try:
                doc = cls._ner_pipeline(text[:5000])
                entities = []
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "GPE", "PERSON", "PRODUCT", "LAW", "MONEY"]:
                        entities.append({
                            "text": ent.text,
                            "label": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                        })
                return entities
            except Exception as e:
                logger.warning(f"NER failed: {e}")
        
        return []

    @classmethod
    def classify_impact(cls, text: str) -> Dict:
        """Classify policy/news impact type and severity."""
        text_lower = text.lower()
        
        # Detect policy type
        if any(w in text_lower for w in ["tariff", "duty", "import tax", "customs"]):
            policy_type = "tariff"
        elif any(w in text_lower for w in ["subsidy", "incentive", "grant", "benefit"]):
            policy_type = "subsidy"
        elif any(w in text_lower for w in ["ban", "prohibit", "restrict", "block"]):
            policy_type = "restriction"
        elif any(w in text_lower for w in ["regulation", "standard", "compliance", "requirement"]):
            policy_type = "regulation"
        else:
            policy_type = "other"
        
        # Detect severity keywords
        high_severity = ["critical", "significant", "major", "substantial", "severe"]
        medium_severity = ["moderate", "notable", "considerable", "meaningful"]
        
        if any(w in text_lower for w in high_severity):
            severity = "high"
        elif any(w in text_lower for w in medium_severity):
            severity = "medium"
        else:
            severity = "low"
        
        return {"policy_type": policy_type, "severity": severity}
