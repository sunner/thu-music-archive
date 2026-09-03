import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from archive.models import Artist, Song
from archive.netease import NeteaseClient

class Command(BaseCommand):
    help = '从网易云音乐公开接口爬取歌曲与歌手元数据。'
    def add_arguments(self, parser):
        parser.add_argument('playlist_id', type=int, help='网易云歌单 ID')
        parser.add_argument('--limit', type=int, default=100)
        parser.add_argument('--delay', type=float, default=1.0)
        parser.add_argument('--cache', default='data/cache/netease')
    def handle(self, *args, **options):
        if options['limit'] < 1: raise CommandError('--limit 必须为正数')
        client = NeteaseClient(options['delay'])
        try: songs = client.playlist(options['playlist_id'], options['limit'])
        except Exception as exc: raise CommandError(f'网易云请求失败：{exc}') from exc
        cache = Path(options['cache']); cache.mkdir(parents=True, exist_ok=True)
        (cache / f"playlist-{options['playlist_id']}.json").write_text(json.dumps(songs, ensure_ascii=False, indent=2), encoding='utf-8')
        created = 0
        for item in songs:
            artist, _ = Artist.objects.get_or_create(name=item['artist'], defaults={'image_url': '', 'source_url': 'https://music.163.com/'})
            _, was_created = Song.objects.get_or_create(title=item['title'], artist=artist, defaults={k: item[k] for k in ('lyrics', 'image_url', 'source_url')})
            created += was_created
        self.stdout.write(self.style.SUCCESS(f'网易云爬取 {len(songs)} 首，新增 {created} 首；缓存已写入 {cache}'))
