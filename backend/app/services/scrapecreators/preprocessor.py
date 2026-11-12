import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Modificadores de busca orientados a atritos, problemas e intenção de compra
PAIN_MODIFIERS = [
    "problema",
    "reclamacao",
    "dificuldade",
    "cancelar",
    "ruim",
    "caro",
    "falha",
    "dor de cabeca",
    "pior"
]

NOISE_WORDS = {
    "show", "top", "parabens", "otimo", "bom", "legal", "valeu", "obrigado",
    "obrigada", "amei", "lindo", "perfeito", "deus abencoe", "amem", "muito bom",
    "inscrito", "sucesso"
}


class MiningPreprocessor:
    """
    Camada de inteligência de busca e filtragem:
    1. Query Expansion: Gera termos adicionais com foco em atrito e queixas reais.
    2. Comment Cleansing: Remove ruído (elogios superficiais, spam, comentários monossilábicos).
    3. Sentiment Scoring: Prioriza menções que expressam frustração ou perda financeira.
    """

    @classmethod
    def expand_queries(cls, base_keyword: str, niche_name: Optional[str] = None, max_queries: int = 3) -> List[str]:
        """
        Gera variações de busca focadas em dor e problemas operacionais.
        Ex: 'software clinica' -> ['software clinica', 'software clinica problema reclamacao', 'software clinica cancelar']
        """
        clean_keyword = base_keyword.strip()
        queries = [clean_keyword]

        # Variação 1: Focada em problemas e reclamações
        queries.append(f"{clean_keyword} problema reclamacao")

        # Variação 2: Focada em custo, cancelamento ou perda de tempo
        queries.append(f"{clean_keyword} cancelar dor de cabeca")

        return queries[:max_queries]

    @classmethod
    def score_comment_relevance(cls, content: str) -> float:
        """
        Calcula pontuação de relevância de 0.0 a 10.0 para um comentário minerado.
        Comentários com palavras de dor ganham peso alto; elogios vazios são penalizados.
        """
        text = content.lower().strip()
        length = len(text)

        # Muito curto = irrelevante
        if length < 15:
            return 0.0

        score = 2.0  # Pontuação base

        # Bônus por tamanho substantivo (explicação detalhada)
        if 40 <= length <= 400:
            score += 2.0
        elif length > 400:
            score += 1.0

        # Penalidade por ruído/elogio vazio
        if any(noise in text for noise in NOISE_WORDS) and length < 50:
            score -= 2.0

        # Bônus por marcadores fortes de dor / atrito
        matches = [mod for mod in PAIN_MODIFIERS if mod in text]
        score += min(len(matches) * 2.5, 6.0)

        # Bônus se menciona perda financeira ou concorrente
        if any(w in text for w in ["preco", "custo", "pagar", "mensalidade", "plataforma", "sistema", "app", "suporte"]):
            score += 1.5

        return max(0.0, min(score, 10.0))

    @classmethod
    def filter_and_rank_comments(
        cls,
        interactions: List[Dict[str, Any]],
        min_score: float = 2.0,
        max_output: int = 40
    ) -> List[Dict[str, Any]]:
        """
        Filtra comentários irrelevantes e ordena os mais informativos e críticos no topo.
        """
        scored_items = []
        for item in interactions:
            content = item.get("content") or ""
            score = cls.score_comment_relevance(content)
            if score >= min_score:
                item_copy = dict(item)
                item_copy["relevance_score"] = score
                scored_items.append(item_copy)

        # Ordena por relevância decrescente e likes
        scored_items.sort(key=lambda x: (x.get("relevance_score", 0), x.get("likes", 0)), reverse=True)
        return scored_items[:max_output]
