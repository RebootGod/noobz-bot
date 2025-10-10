"""
TMDB Episode Runtime Service - Ambil dan hitung rata-rata runtime episode untuk TV series.
Modular sesuai workinginstructions.md.
"""

import logging
from typing import List, Optional
from services.tmdb_base import TMDBBase

logger = logging.getLogger(__name__)

class TMDEpisodeRuntime(TMDBBase):
    """
    Service untuk ambil dan hitung rata-rata runtime episode dari TMDB.
    """
    async def get_average_episode_runtime(self, tv_id: int, seasons: List[dict]) -> Optional[int]:
        """
        Ambil semua episode runtime dari semua season dan hitung rata-rata.
        Args:
            tv_id: TMDB TV series ID
            seasons: List of season dict dari TMDB (movie_info['seasons'])
        Returns:
            Rata-rata runtime (menit) atau None jika tidak ada data
        """
        runtimes = []
        try:
            for season in seasons:
                season_number = season.get('season_number')
                if not season_number or season_number == 0:
                    continue  # Skip specials
                try:
                    endpoint = f"/tv/{tv_id}/season/{season_number}"
                    season_data = await self._make_request(endpoint, {'language': 'id-ID'})
                    episodes = season_data.get('episodes', [])
                    for ep in episodes:
                        rt = ep.get('runtime')
                        if isinstance(rt, int) and rt > 0:
                            runtimes.append(rt)
                except Exception as e:
                    logger.warning(f"Failed to fetch season {season_number} for tv_id {tv_id}: {e}")
                    continue
            if runtimes:
                avg_runtime = round(sum(runtimes) / len(runtimes))
                return avg_runtime
            return None
        finally:
            await self.close()

def get_tmdb_episode_runtime_service():
    return TMDEpisodeRuntime()
