import scipy.stats

from django.http import Http404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import UserSerializer, ScoresSerializer

from users.models import User, Scores


GAME_NAME_TO_INTERNAL = {
    'numberMemory': 'number_memory',
    'chimpTest': 'chimp_test',
    'reactionTime': 'reaction_time',
}


class UserViewSet(mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  GenericViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            return super(UserViewSet, self).update(request, *args, **kwargs)
        except Http404:
            return self.create(request, *args, **kwargs)

    def add_with_ratio(self, result, scores, total, game_name, filter_kwarg):
        item = {
            'score': scores[game_name],
        }

        if scores[game_name] is None:
            item['ratio'] = None
        else:
            if game_name == 'numberMemory':
                item['ratio'] = scipy.stats.norm.cdf(scores[game_name], loc=8.2, scale=2) * 100
            elif game_name == 'chimpTest':
                item['ratio'] = scipy.stats.norm.cdf(scores[game_name], loc=9.8, scale=2) * 100
            else:
                item['ratio'] = (1 - scipy.stats.exponnorm.cdf(scores[game_name], 2.2, loc=200, scale=40)) * 100

        result[game_name] = item

    def update_score(self, scores, new_scores, game_name, best):
        if game_name in new_scores and new_scores[game_name] is not None:
            if scores[game_name] is not None:
                scores[game_name] = best(scores[game_name], new_scores[game_name])
            else:
                scores[game_name] = new_scores[game_name]
        elif scores[game_name] is None:
            scores.pop(game_name)

    @action(detail=True, methods=['get', 'post'])
    def scores(self, request, pk=None):
        user = self.get_object()
        latest_scores = user.get_latest_scores()
        latest_scores_data = ScoresSerializer(latest_scores).data

        if request.method == 'GET':
            response_data = {}
            total_scores = Scores.objects.filter(latest=True).count()

            self.add_with_ratio(response_data, latest_scores_data, total_scores, 'numberMemory', 'number_memory__lt')
            self.add_with_ratio(response_data, latest_scores_data, total_scores, 'chimpTest', 'chimp_test__lt')
            self.add_with_ratio(response_data, latest_scores_data, total_scores, 'reactionTime', 'reaction_time__gt')

            return Response(response_data)

        elif request.method == 'POST':
            self.update_score(latest_scores_data, request.data, 'numberMemory', max)
            self.update_score(latest_scores_data, request.data, 'chimpTest', max)
            self.update_score(latest_scores_data, request.data, 'reactionTime', min)

            serializer_instace = ScoresSerializer(data=latest_scores_data)
            serializer_instace.is_valid(raise_exception=True)

            serializer_instace.save()
            latest_scores.latest = False
            latest_scores.save(update_fields=['latest'])

            return Response(serializer_instace.data)

    def get_leaderboard_from_data(self, data, game_name):
        users = []
        for raw_user_data in data:
            try:
                user = User.objects.get(phone=raw_user_data['phone'])
            except User.DoesNotExist:
                continue
            score = getattr(user.get_latest_scores(), game_name, None)
            if score is None:
                continue

            user_data = UserSerializer(user).data
            user_data['score'] = score
            users.append(user_data)

        if game_name == 'reaction_time':
            result = sorted(users, key=lambda k: k['score'])
        else:
            result = sorted(users, key=lambda k: -k['score'])

        return result

    @action(detail=True)
    def leaderboard(self, request, pk=None):
        user = self.get_object()
        game_name = request.data['gameName']
        game_name = GAME_NAME_TO_INTERNAL[game_name]
        contacts_data = request.data['contacts']
        contacts_data.append(UserSerializer(user).data)

        leaderboard = self.get_leaderboard_from_data(contacts_data, game_name)

        return Response(leaderboard)
