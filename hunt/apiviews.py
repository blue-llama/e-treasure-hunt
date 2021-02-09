from uuid import uuid4

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from hunt.apimixin import AllowPUTAsCreateMixin
from hunt.constants import HINTS_PER_LEVEL
from hunt.models import Hint, Level

EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png"}


class HintSerializer(serializers.HyperlinkedModelSerializer):  # type: ignore
    class Meta:
        model = Hint
        fields = [
            "level",
            "number",
            "image",
        ]


class LevelSerializer(serializers.HyperlinkedModelSerializer):  # type: ignore
    hints = HintSerializer(many=True, read_only=True)

    class Meta:
        model = Level
        fields = [
            "number",
            "name",
            "description",
            "latitude",
            "longitude",
            "tolerance",
            "hints",
        ]


class HintViewSet(AllowPUTAsCreateMixin, viewsets.ModelViewSet):  # type: ignore
    queryset = Hint.objects.all().order_by("level", "number")
    serializer_class = HintSerializer


class LevelViewSet(AllowPUTAsCreateMixin, viewsets.ModelViewSet):  # type: ignore
    queryset = Level.objects.all().order_by("number")
    serializer_class = LevelSerializer

    @action(
        detail=True,
        methods=["put"],
        url_path="hints/(?P<number>\\d+)",
        parser_classes=[FormParser, MultiPartParser],
    )  # type: ignore
    def save_hint(self, request: Request, pk: str, number: str) -> Response:
        # Check that it's a sensible hint.
        if int(number) >= HINTS_PER_LEVEL:
            return Response(
                f"Hint {number} is too high", status=status.HTTP_400_BAD_REQUEST
            )

        # Check that we have a file, and that it seems to be an image.
        upload = next(request.data.values(), None)
        if upload is None:
            return Response("no file attached", status=status.HTTP_400_BAD_REQUEST)

        extension = EXTENSIONS.get(upload.content_type)
        if extension is None:
            return Response(
                f"bad content type: {upload.content_type}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the level.
        try:
            level = Level.objects.get(number=pk)
        except Level.DoesNotExist:
            return Response(
                f"Level {pk} not found",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the old hint, if it exists, else create a new one.
        try:
            hint = level.hints.get(number=number)
            hint.image.delete()
        except Hint.DoesNotExist:
            hint = Hint(level=level, number=number)

        filename = str(uuid4()) + extension
        hint.image.save(filename, upload.file)

        serializer = HintSerializer(hint, context={'request': request})
        return Response(serializer.data)
