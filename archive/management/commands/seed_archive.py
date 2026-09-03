from django.core.management.base import BaseCommand
from archive.models import Artist, Song

class Command(BaseCommand):
    help = 'Create a stable local demonstration dataset.'
    def handle(self, *args, **kwargs):
        if Artist.objects.exists():
            self.stdout.write('Dataset already exists.')
            return
        artists = [Artist.objects.create(name=f'校园音乐人 {i:03d}', bio='来自清华园音乐档案的公开人物资料。', image_url=f'https://picsum.photos/seed/artist{i}/600/600', source_url='https://music.163.com/') for i in range(1, 121)]
        for i in range(1, 2401):
            artist = artists[(i - 1) % len(artists)]
            Song.objects.create(title=f'园中声响 · {i:04d}', artist=artist, lyrics=f'清华园的风穿过树影，留下第 {i} 首歌的回声。', image_url=f'https://picsum.photos/seed/song{i}/800/800', source_url='https://music.163.com/')
        self.stdout.write(self.style.SUCCESS('Created 2,400 songs and 120 artists.'))
