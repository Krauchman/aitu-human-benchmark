from django.http import Http404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from users.serializers import UserSerializer

from users.models import User


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
