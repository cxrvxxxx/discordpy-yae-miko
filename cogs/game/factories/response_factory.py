from abc import ABCMeta

from typing import Dict

from ..objects.response import Response

class ResponseFactory(ABCMeta):
    @staticmethod
    def generate_response(success: bool, data: Dict) -> Response:
        return Response(
            success,
            data
        )
