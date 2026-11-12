import logging
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.services.scrapecreators.preprocessor import MiningPreprocessor

logger = logging.getLogger(__name__)


class ScrapeCreatorsClient:
    """
    Cliente de integração multi-plataforma com a API ScrapeCreators (YouTube, Reddit, TikTok).
    Minera posts e comentários reais de usuários com pré-processamento inteligente de dores.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.SCRAPECREATORS_API_KEY
        self.base_url = (base_url or settings.SCRAPECREATORS_BASE_URL).rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def search_youtube_videos(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Busca vídeos no YouTube relacionados à palavra-chave."""
        if not self.is_configured():
            return []

        url = f"{self.base_url}/v1/youtube/search?query={urllib.parse.quote(query)}"
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    videos = data.get("videos", [])
                    return videos[:limit]
                logger.warning(f"Falha ao buscar videos no YouTube ({res.status_code}): {res.text[:100]}")
        except Exception as e:
            logger.error(f"Erro de conexao com ScrapeCreators YouTube Search: {e}")
        return []

    async def get_youtube_comments(self, video_url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Minera comentários de um vídeo do YouTube."""
        if not self.is_configured():
            return []

        endpoint = f"{self.base_url}/v1/youtube/video/comments?url={urllib.parse.quote(video_url)}&order=top"
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(endpoint, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    comments = data.get("comments", [])
                    return comments[:limit]
                logger.warning(f"Falha ao buscar comentarios no YouTube ({res.status_code}): {res.text[:100]}")
        except Exception as e:
            logger.error(f"Erro ao extrair comentarios do YouTube: {e}")
        return []

    async def search_reddit_discussions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Minera discussões e desabafos de usuários no Reddit."""
        if not self.is_configured():
            return []

        endpoint = f"{self.base_url}/v1/reddit/search?query={urllib.parse.quote(query)}"
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(endpoint, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    posts = data.get("posts", [])
                    discussions = []
                    for post in posts[:limit]:
                        selftext = post.get("selftext", "") or ""
                        title = post.get("title", "")
                        # Conteúdo pode ser a descrição ou a junção do título com o selftext
                        full_content = f"{title}. {selftext}".strip()
                        if len(full_content) > 20:
                            discussions.append({
                                "source": "reddit",
                                "author": post.get("author", "redditor"),
                                "content": full_content,
                                "likes": post.get("score", 0),
                                "post_title": title,
                                "post_url": f"https://reddit.com{post.get('permalink')}" if post.get("permalink") else ""
                            })
                    return discussions
                logger.warning(f"Falha ao buscar no Reddit ({res.status_code}): {res.text[:100]}")
        except Exception as e:
            logger.error(f"Erro ao buscar no Reddit: {e}")
        return []

    async def search_tiktok_insights(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Minera posts e relatos de criadores no TikTok."""
        if not self.is_configured():
            return []

        endpoint = f"{self.base_url}/v1/tiktok/search/keyword?query={urllib.parse.quote(query)}"
        headers = {"x-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(endpoint, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    items = data.get("search_item_list", [])
                    insights = []
                    for item in items[:limit]:
                        aweme = item.get("aweme_info", {})
                        desc = aweme.get("desc", "")
                        if desc and len(desc.strip()) > 15:
                            insights.append({
                                "source": "tiktok",
                                "author": aweme.get("author", {}).get("nickname", "tiktoker"),
                                "content": desc.strip(),
                                "likes": aweme.get("statistics", {}).get("digg_count", 0),
                                "post_title": desc[:40],
                                "post_url": ""
                            })
                    return insights
                logger.warning(f"Falha ao buscar no TikTok ({res.status_code}): {res.text[:100]}")
        except Exception as e:
            logger.error(f"Erro ao buscar no TikTok: {e}")
        return []

    async def mine_social_discussions(
        self,
        keyword: str,
        niche_name: Optional[str] = None,
        max_interactions: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Orquestra a busca de discussões reais cruzando YouTube, Reddit e TikTok com expansão de query e filtro de ruído.
        """
        if not self.is_configured():
            logger.info("ScrapeCreators API Key nao configurada. Pulando mineracao ao vivo.")
            return []

        raw_interactions: List[Dict[str, Any]] = []

        # 1. Gera termos expandidos focados em queixas/dores
        expanded_queries = MiningPreprocessor.expand_queries(keyword, niche_name=niche_name)
        logger.info(f"Termos expandidos para busca social: {expanded_queries}")

        try:
            # 2. Mineração Reddit (Comunidades & Desabafos de problemas)
            reddit_items = await self.search_reddit_discussions(keyword, limit=6)
            raw_interactions.extend(reddit_items)
            logger.info(f"Reddit: coletadas {len(reddit_items)} discussões")

            # 3. Mineração YouTube (Comentários de vídeos relevantes)
            # Pesquisa com o termo original e termo focado em problema
            for q in expanded_queries[:2]:
                videos = await self.search_youtube_videos(q, limit=2)
                for vid in videos:
                    vid_url = vid.get("url")
                    vid_title = vid.get("title", "Video")
                    if not vid_url:
                        continue

                    comments = await self.get_youtube_comments(vid_url, limit=15)
                    for c in comments:
                        content = c.get("content") or c.get("text")
                        if content and len(content.strip()) > 10:
                            raw_interactions.append({
                                "source": "youtube",
                                "author": c.get("author", {}).get("name", "Usuario"),
                                "content": content.strip(),
                                "likes": c.get("engagement", {}).get("likes", 0),
                                "post_title": vid_title,
                                "post_url": vid_url
                            })

            # 4. Mineração TikTok (Trends & relatos de usuários)
            tiktok_items = await self.search_tiktok_insights(keyword, limit=5)
            raw_interactions.extend(tiktok_items)
            logger.info(f"TikTok: coletados {len(tiktok_items)} relatos")

        except Exception as err:
            logger.error(f"Erro durante ciclo de mineracao social real: {err}")

        # 5. Pré-processamento: Eliminação de ruído, cálculo de relevância e ranking
        filtered_interactions = MiningPreprocessor.filter_and_rank_comments(
            raw_interactions,
            min_score=1.5,
            max_output=max_interactions
        )
        logger.info(f"Mineração finalizada: {len(raw_interactions)} brutos -> {len(filtered_interactions)} relevantes qualificados.")

        return filtered_interactions
