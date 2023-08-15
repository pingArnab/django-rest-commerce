from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Carousel, SubHeading
from .serializers import BannersSerializer


@api_view(['GET'])
def get_all_banners(request):
    carousel_qs = Carousel.objects.all().order_by('seq_no')
    return Response(BannersSerializer(carousel_qs, many=True).data)


@api_view(['GET'])
def get_all_sub_banners(request):
    sub_heading_qs = SubHeading.objects.all().order_by('seq_no')
    return Response(BannersSerializer(sub_heading_qs, many=True).data)
