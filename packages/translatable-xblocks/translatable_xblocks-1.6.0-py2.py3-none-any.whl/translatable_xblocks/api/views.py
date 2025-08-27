"""
Views for the Translatable XBlocks API
"""

import logging

from django.conf import settings
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from requests.exceptions import Timeout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from translatable_xblocks.ai_translations_service import AiTranslationService
from translatable_xblocks.config import TranslatableXBlocksFeatureConfig as Config
from translatable_xblocks.platform_imports import (
    get_transcript_languages_val,
    get_user_role,
)

logger = logging.getLogger(__name__)


class ConfigAPI(APIView):
    """Get / Set configuration for the translations feature."""

    permission_classes = (IsAuthenticated,)

    ai_translations_service = AiTranslationService()

    def get(self, request):
        """
        List feature configuration
        """

        # Lookup course from request
        course_id = request.GET.get("course_id")
        if not course_id:
            return HttpResponseBadRequest("course_id is required")
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return HttpResponseBadRequest(f"Invalid course course_id: {course_id}")

        # Check that feature is enabled
        feature_available = Config.xpert_translations_available_for_course(course_key)
        feature_enabled = Config.xpert_translations_enabled_for_course(course_key)

        # Get available translation languages
        try:
            available_translation_languages = (
                self.ai_translations_service.get_course_translation_languages(course_id)
            )
        except Timeout:
            exception_string = f"Timeout occurred while getting translation languages for course: {course_id}"
            logger.error(exception_string)
            return Response(
                {"message": exception_string},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        # Return Data
        return Response(
            {
                "available_translation_languages": available_translation_languages,
                "feature_available": feature_available,
                "feature_enabled": feature_enabled,
                "transcription_languages": get_transcript_languages_val(
                    course_id, settings.AI_TRANSCRIPTS_PROVIDER_TYPE
                ),
            }
        )

    def post(self, request):
        """
        Set feature configuration.
        """

        # Check correct POST body
        if "course_id" not in request.data:
            return HttpResponseBadRequest("course_id is required")
        if "feature_enabled" not in request.data:
            return HttpResponseBadRequest("feature_enabled is required")

        # Pull args from body
        course_id = request.data.get("course_id")
        feature_enabled = request.data.get("feature_enabled")
        available_translation_languages = request.data.get(
            "available_translation_languages"
        )

        # Validate course key
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return HttpResponseBadRequest(f"Invalid course course_id: {course_id}")

        # Check user has instructor / staff permissions
        if get_user_role(request.user, course_key) not in ("staff", "instructor"):
            return HttpResponseForbidden()

        # Set new feature value
        try:
            Config.enable_xpert_translations_for_course(course_key, feature_enabled)

        except ValueError:
            return Response(
                {
                    "available_translation_languages": [],
                    "feature_available": Config.xpert_translations_available_for_course(
                        course_key
                    ),
                    "feature_enabled": Config.xpert_translations_enabled_for_course(
                        course_key
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If language config was provided, set those available languages using ai_translations_service
        if available_translation_languages and len(available_translation_languages):
            post_data = {
                "course_id": course_id,
                "available_unit_translation_languages": available_translation_languages,
            }
            available_translation_languages = (
                self.ai_translations_service.post_course_translation_languages(
                    post_data
                )
            )
        # Otherwise, just get existing language config state
        else:
            available_translation_languages = (
                self.ai_translations_service.get_course_translation_languages(course_id)
            )

        return Response(
            {
                "available_translation_languages": available_translation_languages,
                "feature_available": Config.xpert_translations_available_for_course(
                    course_key
                ),
                "feature_enabled": Config.xpert_translations_enabled_for_course(
                    course_key
                ),
            },
            status=status.HTTP_201_CREATED,
        )
