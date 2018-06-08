import json

import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum

from app.models import Poster, Vote, Event, Score, RefereeMapping
from app.exceptions import OverScoreException, NeedRefereePermissinException,\
    VotingUnavailableException, NeedSciPermissionException, VoteLimitationException

reward_thresh = [48, 44, 40]
reward_thresh_des = ["ดีเยี่ยม", "ดีมาก", "ดี"]

User = get_user_model()

def is_sci_member(user):
    return user.is_sci_member


@login_required
def logout(request):
    auth_logout(request)
    #
    # !!! CHANGE HOST ADDR (part of)
    #
    return HttpResponseRedirect('https://api.tu.ac.th/logout/?next={}'.format(
        request.META['HTTP_REFERER']
    ))



def home(request, event_pk=1):
    if request.method == "GET":
        event = Event.objects.get(pk=event_pk)
        votes = list()
        top_votes = Poster.objects.filter(event=event).annotate(
            vote_count=Count('vote', filter=Q(vote__is_use=True))
        ).order_by("-vote_count")[:10]
        if request.user.is_authenticated and request.user.is_sci_member:
            user = request.user
            qs = Vote.objects.filter(user=user, is_use=True)
            if qs.exists():
                votes = qs
        context = {
            'votes': votes,
            'vote_count': len(votes),
            'max_vote': event.max_vote,
            'top_votes': top_votes,
        }
        return render(request, 'app/home.html', context)

@login_required
@user_passes_test(lambda x: x.is_staff)
def get_report(request, event_pk=1):
    event = Event.objects.get(pk=event_pk)
    if request.method == 'GET':
        posters = list(Poster.objects.filter(event=event).values(
            'poster_id', 'score__question', 'title',
        ).annotate(
            avg_score=Avg('score__value', filter=Q(score__question__is_use=True))
        ).order_by('-avg_score'))

        posters = pd.DataFrame(posters)
        posters = posters.groupby(['poster_id',])
        rewards = [ list() for _ in reward_thresh ]
        for name, group in posters:
            if name == "SP_tech606111":
                print(group)
            score = group.avg_score.sum()
            for threshold in reward_thresh:
                if score >= threshold:
                    rewards[reward_thresh.index(threshold)].append({
                        'poster_id': name,
                        'title': group.iloc[0]['title'],
                        'score': score,
                    })
                    break

        des = ["รางวัลระดับ{} (มากกว่า {} คะแนน)".format(d, s)
            for d, s in zip(reward_thresh_des, reward_thresh)]

        top_votes = Poster.objects.filter(event=event).annotate(
            vote_count=Count('vote', filter=Q(vote__is_use=True))
        ).order_by("-vote_count")[:10]
        context = {
            'top_votes': top_votes,
            'rewards': zip(des,  rewards),
        }
        return render(request, 'app/report.html', context)


def all_qr(request):
    qs = Poster.objects.filter(event__pk=1).values('id', 'poster_id', 'title')
    lqs = list(Poster.objects.filter(event__pk=1).values('id', 'poster_id', 'title'))
    pages = list()
    for i in range(0, len(qs), 4):
        p = list()
        for j in range(4):
            p.append( lqs[i+j])
        pages.append( p )
    ids = [x[0] for x in qs.values_list('id')]
    context = {
        'posters': qs,
        'pages': pages,
        'ids': ids,
    }
    return render(request, "app/all_qr.html", context)

def get_qr(request, posterid=None):
    if not posterid:
        qs = Poster.objects.all()
        return render(request, 'app/qr-list.html', {'posters':qs})
    else:
        try:
            poster = Poster.objects.get(pk=posterid)
            return render(request, 'app/getqr.html', {'poster': poster})
        except Poster.DoesNotExist:
            return HttpResponse(status='404')


@login_required
def poster_detail(request, pk):
    if request.method == 'GET':
        poster = Poster.objects.get(pk=pk)
        total_vote = poster.vote_set.filter(is_use=True).count()
        vote = Vote.objects.filter(user=request.user, poster=poster)
        if vote.exists():
            vote = vote[0].is_use
        else:
            vote = False

        judgeable = False
        if hasattr(request.user, 'refereemapping') and\
                request.user.refereemapping in poster.referees.all():
            judgeable = True

        return render(request, 'app/poster-detail.html', {
            'poster': poster,
            'totalvote': total_vote,
            'vote': vote,
            'judgeable': judgeable,
        })


@login_required
def question(request, pk):
    if request.method == 'GET':
        poster = Poster.objects.get(pk=pk)
        ref = RefereeMapping.objects.get(user=request.user)
        if not ref in poster.referees.all():
            return HttpResponse("Need permission to view this page.", status=403)
        event = poster.event
        questions = list(event.get_available_question().values('id', 'message', 'max_score'))
        return render(request, 'app/question.html',
                      {'poster': poster, 'event': event,
                        'questions': questions, })


def get_question_detail(request, pk):
    if request.method == 'GET':
        ref = RefereeMapping.objects.get(user=request.user)
        poster = Poster.objects.get(pk=pk)
        event = Event.objects.get(pk=1)
        score_list = Score.objects.filter(referee=ref, poster=poster)
        questions = list(event.get_available_question().values(
            'id', 'message', 'max_score'))
        scores = {q['id']: 0 for q in questions}
        for score in score_list:
            scores[score.question.id] = score.value
        context = {}
        context['scores'] = scores
        context['questions'] = questions
        return JsonResponse(context, safe=False)


@login_required
@user_passes_test(is_sci_member)
def vote(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf8'))
        data['user'] = User.objects.get(pk=data['user'])
        data['poster'] = Poster.objects.get(pk=data['poster'])
        vote, created = Vote.objects.get_or_create(user=data['user'], poster=data['poster'])
        if not created:
            vote.is_use = not vote.is_use
            vote.save()
        total_vote = data['poster'].vote_set.filter(is_use=True).count()
        context = {'isLike': vote.is_use, 'totalvote': total_vote}
        return JsonResponse(context, status=200)


@login_required
@transaction.atomic
def scoring(request):
    if request.method == 'POST':
        payload = {}
        context = json.loads(request.body.decode())
        ref = RefereeMapping.objects.get(user__pk=context['user'])
        poster = Poster.objects.get(pk=context['poster'])
        event = Event.objects.get(pk=context['event'])
        err_message = list()
        for question in event.get_available_question():
            value = context['scores'][str(question.id)]
            try:
                score, _ = Score.objects.update_or_create(
                    poster=poster, question=question, referee=ref,
                    defaults={'value': value})
                payload[score.question.id] = {
                    'question': score.question.id,
                    'referee': score.referee.id,
                    'value': score.value,
                }
            except OverScoreException as err:
                err_message.append({
                    "question": question.id,
                    "message": str(err)
                })
        if err_message:
            return JsonResponse(err_message, status=500, safe=False)
        else:
            return JsonResponse(payload, status=200, safe=True)
