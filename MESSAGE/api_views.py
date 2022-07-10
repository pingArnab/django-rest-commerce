import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from DRC.core.exceptions import ErrorResponse, DataNotFoundException
from DRC.core.DRCConstant import ErrorCode, ErrorMessage
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity, TrigramDistance
from rest_framework import pagination

from PRODUCT.utils import product_filter_with_query_parameter
from .models import Message
from .serializers import MessageListSerializer
from DRC.settings import PROJECT_NAME
from DRC.core.permissions import UserOnly

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 2
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 1000


@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def all_msg_by_user(request):
    msgs = Message.objects.filter(receiver=request.user).order_by('timestamp')
    if request.GET.get('status') == 'unread':
        msgs = msgs.filter(read_status=False)
    elif request.GET.get('status') == 'read':
        msgs = msgs.filter(read_status=True)
    if request.GET.get('page_size'):
        paginator = pagination.PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size')
        paginated_msgs = paginator.paginate_queryset(msgs, request)
        return paginator.get_paginated_response(MessageListSerializer(paginated_msgs, many=True).data)
    return Response(MessageListSerializer(msgs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def msg_by_id(request, msg_id):
    msg = Message.objects.filter(
        message_id=str(msg_id).strip()
    ).filter(
        Q(receiver=request.user) | Q(sender=request.user)
    )
    if not msg:
        return Response({
            'error': {
                'code': 404,
                'message': 'Message not found'
            }
        }, status=400)
    return Response(MessageListSerializer(msg.first(), many=False).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, UserOnly])
def mark_msg_as_read(request, msg_id):
    FUNCTION_NAME = 'mark_msg_as_read'
    try:
        msg = Message.objects.get(
            message_id=str(msg_id).strip(),
            receiver=request.user
        )
        msg.read_status = True
        msg.save()
    except Exception as ex:
        logger.warning(FUNCTION_NAME + ' -> Exception found: ' + ex.__str__())
        return Response({
            'error': {
                'code': 404,
                'message': 'Message not found'
            }
        }, status=400)
    return Response(MessageListSerializer(msg, many=False).data)
