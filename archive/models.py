from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=120, unique=True)
    image_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    class Meta:
        ordering = ['name']
    def __str__(self): return self.name

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    lyrics = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
        indexes = [models.Index(fields=['title']), models.Index(fields=['artist', 'title'])]
    def __str__(self): return self.title

class Comment(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
