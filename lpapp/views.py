import math
from hashlib import md5
from datetime import datetime
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
from models import *


def get_uniq_hash(request):
    uniq_hash = md5(str(datetime.now()) + request.user.username).hexdigest()[:7]
    return uniq_hash


class MessageListView(generic.ListView):
    template_name = "message_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MessageListView, self).get_context_data(*args, **kwargs)
        context['session_id'] = self.kwargs['session_id']
        context['async_url'] = settings.ASYNC_BACKEND_URL
        return context

    def get_queryset(self):
        return Message.objects.filter(session_id=self.kwargs['session_id'])[:10]


@login_required
def main_view(request):
    session_id = get_uniq_hash(request)
    return redirect('message_view', session_id=session_id)


@login_required
def main_game_view(request):
    session_id = get_uniq_hash(request)
    generate_game(request.user, session_id)
    return redirect('new_game_view', session_id=session_id)


@login_required
def game_view(request, session_id):
    game = Game.objects.get(session_id=session_id)
    if request.user.pk not in game.gamers:
        game.gamers.append(request.user.pk)
    letters_in_row = int(math.sqrt(len(game.letters)))
    variables = {
        'session_id': session_id,
        'async_url': settings.ASYNC_BACKEND_URL,
        'letters': game.to_mongo()['letters'],
        'letters_in_row': letters_in_row,
        'rows_range': xrange(letters_in_row)
    }
    return render(request, 'game.html', variables)


def create_message(request):
    m = Message(
        user=request.user,
        text=request.POST['message_text'],
        session_id=request.POST['session_id'])
    try:
        m.save()
    except Exception as e:
        print str(e)
    return HttpResponse("OK")
