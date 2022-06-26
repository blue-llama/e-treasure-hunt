from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.http import Http404
from rest_framework import status
from rest_framework.request import Request, clone_request
from rest_framework.response import Response

if TYPE_CHECKING:
    from rest_framework.viewsets import GenericViewSet

    _Base = GenericViewSet
else:
    _Base = object


# https://gist.github.com/tomchristie/a2ace4577eff2c603b1b
class AllowPUTAsCreateMixin(_Base):
    """
    The following mixin class may be used in order to support PUT-as-create
    behavior for incoming requests.
    """

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object_or_none()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if instance is None:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            lookup_value = self.kwargs[lookup_url_kwarg]
            extra_kwargs = {self.lookup_field: lookup_value}
            serializer.save(**extra_kwargs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def get_object_or_none(self) -> Any:
        try:
            return self.get_object()
        except Http404:
            if self.request.method == "PUT":
                self.check_permissions(clone_request(self.request, "POST"))
            else:
                raise
