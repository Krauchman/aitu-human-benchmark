from django.http import Http404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import UserSerializer, ScoresSerializer

from users.models import User, Scores


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

        worse = Scores.objects.filter(latest=True, **{filter_kwarg: scores[game_name]}).count()
        item['ratio'] = worse / total if total != 0 else 1

        result[game_name] = item

    @action(detail=True, methods=['get', 'post'])
    def scores(self, request, pk=None):
        user = self.get_object()
        latest_scores = user.get_latest_scores()
        latest_scores_data = ScoresSerializer(latest_scores).data

        if request.method == 'GET':
            response_data = {}
            total_scores = Scores.objects.filter(latest=True).count()

            self.add_with_ratio(response_data, latest_scores_data, total_scores, 'numberMemory', 'number_memory__lt')
            self.add_with_ratio(response_data, latest_scores_data, total_scores, 'reactionTime', 'reaction_time__gt')

            return Response(response_data)

        elif request.method == 'POST':
            if 'numberMemory' in request.data:
                latest_scores_data['numberMemory'] = max(latest_scores_data['numberMemory'], request.data['numberMemory'])

            if 'reactionTime' in request.data:
                latest_scores_data['reactionTime'] = min(latest_scores_data['reactionTime'], request.data['reactionTime'])

            serializer_instace = ScoresSerializer(data=latest_scores_data)
            serializer_instace.is_valid(raise_exception=True)

            serializer_instace.save()
            latest_scores.latest = False
            latest_scores.save(update_fields=['latest'])

            return Response(serializer_instace.data)

