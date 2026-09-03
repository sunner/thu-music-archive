"""网易云音乐公开接口适配器：只采集文字和图片元数据，不下载音视频。"""
import time
from typing import Any

import requests

API = 'https://music.163.com/api'


class NeteaseClient:
    def __init__(self, delay: float = 1.0, retries: int = 3):
        self.delay = max(delay, 0.2)
        self.retries = max(retries, 1)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MusicArchiveStudentCrawler/1.0'})

    def get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """限速请求 JSON；网络错误采用指数退避重试。"""
        error = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(f'{API}{path}', params=params, timeout=20)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                error = exc
                if attempt + 1 < self.retries:
                    time.sleep(self.delay * (2**attempt))
        raise RuntimeError(f'网易云接口请求失败: {path}') from error

    def playlist(self, playlist_id: int, limit: int = 100) -> list[dict[str, Any]]:
        """读取歌单歌曲，并补充歌词和歌手资料。"""
        data = self.get_json('/playlist/detail', {'id': playlist_id})
        tracks = data.get('playlist', {}).get('trackIds', [])[:limit]
        songs = []
        for start in range(0, len(tracks), 100):
            ids = ','.join(str(item['id']) for item in tracks[start:start + 100])
            detail = self.get_json('/song/detail', {'ids': f'[{ids}]'})
            for raw in detail.get('songs', []):
                artists = raw.get('ar') or raw.get('artists') or []
                artist = artists[0] if artists else {}
                artist_id = artist.get('id')
                song_id = raw.get('id')
                artist_info = self.artist(artist_id) if artist_id else {}
                songs.append({'title': raw.get('name', '未命名歌曲'), 'artist': artist.get('name', '未知歌手'), 'artist_id': artist_id, 'image_url': raw.get('al', {}).get('picUrl', ''), 'source_url': f'https://music.163.com/#/song?id={song_id}', 'lyrics': self.lyrics(song_id), 'artist_image_url': artist_info.get('image_url', ''), 'artist_bio': artist_info.get('bio', ''), 'artist_source_url': f'https://music.163.com/#/artist?id={artist_id}'})
        return songs

    def lyrics(self, song_id: int) -> str:
        data = self.get_json('/song/lyric', {'id': song_id, 'lv': 1, 'kv': 1, 'tv': -1})
        text = data.get('lrc', {}).get('lyric', '')
        return '\n'.join(line.split(']', 1)[-1] for line in text.splitlines() if ']' in line)

    def artist(self, artist_id: int) -> dict[str, str]:
        data = self.get_json('/artist/detail', {'id': artist_id})
        artist = data.get('data', {}).get('artist', {})
        return {'image_url': artist.get('cover', ''), 'bio': artist.get('briefDesc', '')}
