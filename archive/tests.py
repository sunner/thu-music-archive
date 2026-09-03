from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Artist, Comment, Song
from .netease import NeteaseClient


class ArchiveViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artists = [Artist.objects.create(name=f'歌手 {i}', bio=f'简介 {i}') for i in range(13)]
        for i in range(25):
            Song.objects.create(
                title=f'歌曲 {i}',
                artist=cls.artists[i % len(cls.artists)],
                lyrics=f'歌词内容 {i}',
                image_url='https://example.com/song.jpg',
                source_url='https://music.163.com/song',
            )

    def test_song_list_is_paginated(self):
        response = self.client.get(reverse('song_list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 12)
        self.assertEqual(response.context['page_obj'].number, 2)

    def test_artist_detail_contains_all_songs(self):
        artist = self.artists[0]
        response = self.client.get(reverse('artist_detail', args=[artist.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['songs']), 2)

    def test_song_detail_can_create_and_delete_comment(self):
        song = Song.objects.first()
        response = self.client.post(reverse('song_detail', args=[song.pk]), {'body': '很喜欢这首歌'})
        self.assertRedirects(response, reverse('song_detail', args=[song.pk]))
        comment = Comment.objects.get(song=song)
        self.client.post(reverse('song_detail', args=[song.pk]), {'action': 'delete', 'comment_id': comment.pk})
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_search_filters_songs_and_reports_time(self):
        response = self.client.get(reverse('search'), {'q': '歌词内容 3', 'kind': 'song'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 1)
        self.assertIn('elapsed_ms', response.context)

    def test_search_filters_artists(self):
        response = self.client.get(reverse('search'), {'q': '简介 2', 'kind': 'artist'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 1)

    def test_empty_search_returns_no_results(self):
        response = self.client.get(reverse('search'), {'q': '不存在的档案', 'kind': 'song'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 0)

    def test_invalid_page_is_clamped_to_last_page(self):
        response = self.client.get(reverse('song_list'), {'page': 'not-a-page'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 1)

    def test_blank_comment_is_not_saved(self):
        song = Song.objects.first()
        self.client.post(reverse('song_detail', args=[song.pk]), {'body': '   '})
        self.assertEqual(Comment.objects.filter(song=song).count(), 0)


class NeteaseCrawlerTests(TestCase):
    @patch('archive.netease.requests.Session')
    def test_playlist_parser_accepts_netease_artist_shape(self, session_cls):
        session = session_cls.return_value
        playlist = Mock(status_code=200)
        playlist.json.return_value = {'playlist': {'trackIds': [{'id': 7}]}}
        detail = Mock(status_code=200)
        detail.json.return_value = {'songs': [{'id': 7, 'name': '春日', 'artists': [{'id': 9, 'name': '测试歌手'}], 'al': {'picUrl': 'https://example.com/a.jpg'}}]}
        lyric = Mock(status_code=200)
        lyric.json.return_value = {'lrc': {'lyric': '[00:01.00]第一句\n[00:02.00]第二句'}}
        artist = Mock(status_code=200)
        artist.json.return_value = {'data': {'artist': {'cover': 'https://example.com/artist.jpg', 'briefDesc': '歌手简介'}}}
        session.get.side_effect = [playlist, detail, artist, lyric]
        songs = NeteaseClient(delay=0).playlist(1, limit=1)
        self.assertEqual(songs[0]['artist'], '测试歌手')
        self.assertEqual(songs[0]['source_url'], 'https://music.163.com/#/song?id=7')
        self.assertEqual(songs[0]['lyrics'], '第一句\n第二句')
        self.assertEqual(songs[0]['artist_bio'], '歌手简介')

    @patch('archive.management.commands.crawl_netease.NeteaseClient.playlist')
    def test_crawl_command_persists_song_and_artist(self, playlist):
        playlist.return_value = [{'title': '命令测试', 'artist': '命令歌手', 'lyrics': '歌词', 'image_url': 'https://example.com/a.jpg', 'source_url': 'https://music.163.com/#/song?id=1'}]
        call_command('crawl_netease', 123, '--limit', '1', '--cache', '/tmp/music-archive-test-cache')
        self.assertTrue(Song.objects.filter(title='命令测试', artist__name='命令歌手').exists())
