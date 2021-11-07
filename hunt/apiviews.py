from uuid import uuid4

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from hunt.constants import HINTS_PER_LEVEL
from hunt.models import Hint, Level
from hunt.third_party.apimixin import AllowPUTAsCreateMixin

EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png"}


class HintSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hint
        fields = [
            "level",
            "number",
            "image",
        ]


class LevelSerializer(serializers.HyperlinkedModelSerializer):
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


class LevelViewSet(AllowPUTAsCreateMixin, viewsets.ModelViewSet):
    queryset = Level.objects.all().order_by("number")
    serializer_class = LevelSerializer
    http_method_names = ["delete", "get", "head", "patch", "put"]

    @action(
        detail=True,
        methods=["put"],
        url_path="hints/(?P<number>\\d+)",
        parser_classes=[FormParser, MultiPartParser],
    )
    def save_hint(self, request: Request, pk: str, number: str) -> Response:
        # Check that it's a sensible hint.
        if int(number) >= HINTS_PER_LEVEL:
            return Response(
                f"Hint {number} is too high", status=status.HTTP_400_BAD_REQUEST
            )

        # Check that we have a file, and that it seems to be an image.
        upload = next(iter(request.data.values()), None)
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
            return Response(f"Level {pk} not found", status=status.HTTP_404_NOT_FOUND)

        # Update the old hint, if it exists, else create a new one.
        created = False
        try:
            hint = level.hints.get(number=number)
            hint.image.delete()
        except Hint.DoesNotExist:
            hint = Hint(level=level, number=number)
            created = True

        filename = f"{uuid4()}{extension}"
        hint.image.save(filename, upload.file)

        serializer = HintSerializer(hint, context={"request": request})
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)
