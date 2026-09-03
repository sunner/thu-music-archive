import time
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .models import Artist, Comment, Song

def page(request, items, number=12):
    return Paginator(items, number).get_page(request.GET.get('page', 1))

def song_list(request):
    songs = Song.objects.select_related('artist').all()
    return render(request, 'archive/song_list.html', {'page_obj': page(request, songs), 'song_count': songs.count(), 'artist_count': Artist.objects.count(), 'section': 'songs'})

def artist_list(request):
    artists = Artist.objects.all()
    return render(request, 'archive/artist_list.html', {'page_obj': page(request, artists), 'section': 'artists'})

def song_detail(request, pk):
    song = get_object_or_404(Song.objects.select_related('artist'), pk=pk)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            Comment.objects.filter(pk=request.POST.get('comment_id'), song=song).delete()
        elif request.POST.get('body', '').strip():
            Comment.objects.create(song=song, body=request.POST['body'].strip())
        return redirect('song_detail', pk=pk)
    return render(request, 'archive/song_detail.html', {'song': song, 'comments': song.comments.all(), 'section': 'songs'})

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    return render(request, 'archive/artist_detail.html', {'artist': artist, 'songs': artist.songs.all(), 'section': 'artists'})

def search(request):
    query = request.GET.get('q', '').strip()[:20]
    kind = request.GET.get('kind', 'song')
    started = time.perf_counter()
    if kind == 'artist':
        results = Artist.objects.filter(Q(name__icontains=query) | Q(bio__icontains=query)) if query else Artist.objects.none()
    else:
        results = Song.objects.select_related('artist').filter(Q(title__icontains=query) | Q(artist__name__icontains=query) | Q(lyrics__icontains=query)) if query else Song.objects.none()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return render(request, 'archive/search.html', {'page_obj': page(request, results), 'query': query, 'kind': kind, 'elapsed_ms': elapsed_ms, 'result_count': results.count(), 'section': 'search'})
