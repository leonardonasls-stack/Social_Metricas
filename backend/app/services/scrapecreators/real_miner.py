import logging
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScrapeCreatorsClient:
    """
    Cliente de integração direta com a API ScrapeCreators (YouTube, TikTok, Instagram, Reddit).
    Minera posts e comentários reais de usuários para alimentar a inteligência de produto.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.SCRAPECREATORS_API_KEY
        self.base_url = (base_url or settings.SCRAPECREATORS_BASE_URL).rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def search_youtube_videos(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
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
                logger.warning(f"Falha ao buscar videos no YouTube ({res.status_code}): {res.text}")
        except Exception as e:
            logger.error(f"Erro de conexao com ScrapeCreators YouTube Search: {e}")
        return []

    async def get_youtube_comments(self, video_url: str, limit: int = 25) -> List[Dict[str, Any]]:
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
                logger.warning(f"Falha ao buscar comentarios no YouTube ({res.status_code}): {res.text}")
        except Exception as e:
            logger.error(f"Erro ao extrair comentarios do YouTube: {e}")
        return []

    async def mine_social_discussions(self, keyword: str, max_interactions: int = 60) -> List[Dict[str, Any]]:
        """
        Orquestra a busca de discussões reais cruzando YouTube e redes sociais.
        Retorna uma lista padronizada de comentários e interações reais.
        """
        if not self.is_configured():
            logger.info("ScrapeCreators API Key nao configurada. Pulando mineracao ao vivo.")
            return []

        mined_interactions: List[Dict[str, Any]] = []

        try:
            # 1. Busca vídeos reais no YouTube com discussões ativas
            videos = await self.search_youtube_videos(keyword, limit=3)
            logger.info(f"ScrapeCreators encontrou {len(videos)} videos no YouTube para '{keyword}'")

            for vid in videos:
                vid_url = vid.get("url")
                vid_title = vid.get("title", "Video")
                if not vid_url:
                    continue

                comments = await self.get_youtube_comments(vid_url, limit=20)
                logger.info(f"Minerados {len(comments)} comentarios do video: {vid_title[:40]}...")

                for c in comments:
                    content = c.get("content") or c.get("text")
                    if content and len(content.strip()) > 10:
                        mined_interactions.append({
                            "source": "youtube",
                            "author": c.get("author", {}).get("name", "Usuario"),
                            "content": content.strip(),
                            "likes": c.get("engagement", {}).get("likes", 0),
                            "post_title": vid_title,
                            "post_url": vid_url
                        })

                if len(mined_interactions) >= max_interactions:
                    break

        except Exception as err:
            logger.error(f"Erro durante ciclo de mineracao social real: {err}")

        return mined_interactions
