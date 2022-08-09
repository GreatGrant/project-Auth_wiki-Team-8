from django.shortcuts import redirect, render
from django.db.models import Q
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import LibraryPage, CommentReaction
from django.urls import reverse
from django.http import HttpResponseRedirect


def solution(message, K):
    print(len(message))
    if len(message) < K:
        return message
    elif len(message) == K and message[-1] != ' ':
        return message[0: K]
    elif len(message) > K and message[K - 1] == ' ':
        return message[0: K - 1]
    elif message[K] == ' ':
        return message[0: K]
    else:
        i = K - 1
        while i < K:
            if message[i] == ' ':
                return message[0: i]
            i -= 1


class LibrarySearchPage(View):
    def get(self, request, *args, **kwargs):
        if 'q' in request.GET:
            keyword = request.GET.get('q', '')
            if keyword == 'a':
                libraries = LibraryPage.objects.all()
            else:
                libraries = LibraryPage.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(library_language__icontains=keyword)
                )
            found = len(libraries)
            page_num = 7
            page = request.GET.get('page', 1)
            libraries_per_page = Paginator(libraries, page_num)
            try:
                libraries = libraries_per_page.page(page)
            except EmptyPage:
                libraries = libraries_per_page.page(page_num)
            except PageNotAnInteger:
                libraries = libraries_per_page.page(
                    libraries_per_page.num_pages)
            return render(
                request,
                'librarys/search_result.html',
                {
                    'libraries': libraries,
                    'found': found,
                    'title': 'Search results',
                    'page': libraries_per_page
                }
            )
        else:
            return redirect('/')


class LibraryInfo(View):
    def get(self, request, pk):
        library = LibraryPage.objects.get(id=pk)
        library.example_file = open(library.example_file.path, 'r')
        library.example_file = library.example_file.read()
        comments = CommentReaction.objects.filter(library=library)[::-1]
        library1 = library
        library1.description = solution(library1.description, 150)
        if len(comments) > 5:
            comments1 = comments[0:5]
        else:
            comments1 = comments
        return render(
            request,
            'librarys/library_page.html',
            {
                'library': library,
                'comments': comments,
                'library1': library1,
                'comments1': comments1
            }
        )

    def post(self, request, pk):
        library = LibraryPage.objects.get(id=pk)
        comment = CommentReaction(
            comment=request.POST['comment'], library=library, author=request.user)
        comment.save()
        return HttpResponseRedirect(request.path_info)


def dislikes(request, pk):
    if request.method == 'POST':
        library = LibraryPage.objects.get(id=pk)
        library.dislike += 1
        library.save()
    return HttpResponseRedirect(reverse('librarys:search_result', args=[str(pk)]))


def likes(request, pk):
    if request.method == 'POST':
        library = LibraryPage.objects.get(id=pk)
        library.like += 1
        library.save()
    return HttpResponseRedirect(reverse('librarys:search_result', args=[str(pk)]))
