from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from DRC.core.permissions import UserOnly
from .serializers import ProductSearchSuggestionSerializer, ProductListSerializer, CategoryListSerializer, \
    SingleProductSerializer, ReviewSerializer
from PRODUCT.models import Product, Category, Review
from .utils import product_filter_with_query_parameter, count_filter
from DRC.core.exceptions import ErrorResponse, DataNotFoundException
from DRC.core.DRCConstant import ErrorCode, ErrorMessage
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity, TrigramDistance
from rest_framework import pagination


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 2
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 1000


@api_view(['GET'])
def all_categories(request):
    categories_queryset = Category.objects.all()
    response = CategoryListSerializer(
        count_filter(categories_queryset, request.query_params.get('count'))
        , many=True
    )
    return Response(response.data)


@api_view(['GET'])
def all_products(request):
    try:
        if request.query_params.get('page_size'):
            paginator = pagination.PageNumberPagination()
            paginator.page_size = request.query_params.get('page_size')
            result_page_qs = paginator.paginate_queryset(
                product_filter_with_query_parameter(Product.objects.order_by('-product_id'), request.query_params),
                request
            )
            serializer = ProductListSerializer(result_page_qs, many=True, context={'user': request.user})
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                ProductListSerializer(
                    product_filter_with_query_parameter(Product.objects.all(), request.query_params),
                    many=True,
                    context={'user': request.user}
                ).data
            )
    except DataNotFoundException as dnf:
        return ErrorResponse(dnf.code, dnf.message).response


@api_view(['GET'])
def product_by_id(request, product_id: str):
    if Product.objects.filter(product_id=product_id):
        product = Product.objects.get(product_id=product_id)
        response = SingleProductSerializer(product, many=False, context={'user': request.user})
        return Response(response.data)
    else:
        return Response({
            'error': {
                'code': 404,
                'message': 'Product not found'
            }
        }, status=400)


@api_view(['GET'])
def search(request):
    keywords = request.GET.get('q')

    query = SearchQuery(keywords)
    product_name_vector = SearchVector('product_name', weight='A')
    tag_vector = SearchVector('tag', weight='A')
    short_description_vector = SearchVector('short_description', weight='B')
    long_description_vector = SearchVector('long_description', weight='B')

    vectors = product_name_vector + tag_vector + short_description_vector + long_description_vector
    search_qs = Product.objects.annotate(rank=SearchRank(vectors, query)).filter(rank__gt=0).order_by('-rank')

    return Response(
        ProductListSerializer(
            product_filter_with_query_parameter(search_qs, request.query_params),
            many=True,
            context={'user': request.user}
        ).data
    )


@api_view(['GET'])
def search_suggestion(request):
    keyword = request.GET.get('q').strip() if request.GET.get('q') else ''
    if len(keyword) < 3:
        return ErrorResponse(code=400, msg='Please give at least 3 letter for suggestion').response
    search_qs = Product.objects.filter(product_name__icontains=keyword)
    return Response(
        ProductSearchSuggestionSerializer(
            product_filter_with_query_parameter(search_qs, request.query_params),
            many=True,
            context={'user': request.user}
        ).data
    )


@api_view(['GET'])
def reviews(request, product_id):
    if not Product.objects.filter(product_id=product_id):
        ErrorResponse(code=ErrorCode.INVALID_PRODUCT_ID, msg=ErrorMessage.INVALID_PRODUCT_ID)
    product = Product.objects.get(product_id=product_id)
    reviews_qs = product.review_set.all().order_by('timestamp')

    if request.query_params.get('page_size'):
        paginator = pagination.PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size')
        result_page_qs = paginator.paginate_queryset(
            reviews_qs,
            request
        )
        serializer = ReviewSerializer(result_page_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response(
            ReviewSerializer(
                reviews_qs,
                many=True,
                context={'user': request.user}
            ).data
        )


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, UserOnly])
def review(request, product_id):
    if not Product.objects.filter(product_id=product_id):
        return ErrorResponse(code=ErrorCode.INVALID_PRODUCT_ID, msg=ErrorMessage.INVALID_PRODUCT_ID).response
    product = Product.objects.get(product_id=product_id)

    if request.method == 'POST':
        if Review.objects.filter(user_id=request.user.id, product_id=product.product_id):
            return ErrorResponse(code=ErrorCode.REVIEW_ALREADY_GIVEN, msg=ErrorMessage.REVIEW_ALREADY_GIVEN).response
        if not request.data.get('rating'):
            return ErrorResponse(code=ErrorCode.RATING_IS_MANDATORY, msg=ErrorMessage.RATING_IS_MANDATORY).response
        rating = float(request.data.get('rating'))
        if type(rating) == float and not 0 <= rating <= 5:
            return ErrorResponse(
                code=ErrorCode.RATING_MUST_BE_A_FLOAT_BW_0_AND_5,
                msg=ErrorMessage.RATING_MUST_BE_A_FLOAT_BW_0_AND_5
            ).response

        user_review = Review.objects.create(
            user_id=request.user.id,
            product_id=product.product_id,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            rating=rating
        )
        user_review.save()
        current_rating = product.rating
        current_rating_count = product.rating_count
        product.rating = ((current_rating * current_rating_count) + rating) / (current_rating_count+1)
        product.rating_count += 1
        product.save()
        return Response(ReviewSerializer(user_review, many=False).data)

    if request.method == 'PUT':
        if not Review.objects.filter(user_id=request.user.id, product_id=product.product_id):
            return ErrorResponse(code=ErrorCode.REVIEW_NOT_GIVEN, msg=ErrorMessage.REVIEW_NOT_GIVEN).response
        user_review: Review = Review.objects.get(user_id=request.user.id, product_id=product.product_id)
        user_review.title = request.data.get('title', user_review.title)
        user_review.description = request.data.get('description', user_review.description)
        rating = float(request.data.get('rating'))
        if type(rating) == float and not 0 <= rating <= 5:
            return ErrorResponse(
                code=ErrorCode.RATING_MUST_BE_A_FLOAT_BW_0_AND_5,
                msg=ErrorMessage.RATING_MUST_BE_A_FLOAT_BW_0_AND_5
            ).response
        user_review.rating = request.data.get('rating', user_review.rating)
        user_review.save()
        return Response(ReviewSerializer(user_review, many=False).data)
    if request.method == 'DELETE':
        if not Review.objects.filter(user_id=request.user.id, product_id=product.product_id):
            return ErrorResponse(code=ErrorCode.REVIEW_NOT_GIVEN, msg=ErrorMessage.REVIEW_NOT_GIVEN).response
        Review.objects.filter(user_id=request.user.id, product_id=product.product_id).delete()
        return Response({'status': 'success', 'details': 'Review deleted successfully'})
