from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Carousel
from .serializers import CarouselSerializers


@api_view(['GET'])
def get_all_heroes(request):
    carousel_qs = Carousel.objects.all().order_by('seq_no')
    return Response(CarouselSerializers(carousel_qs, many=True).data)
