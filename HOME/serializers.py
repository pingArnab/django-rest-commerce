from rest_framework import serializers
from .models import Carousel


class CarouselSerializers(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Carousel
        fields = (
            'name', 'image', 'target'
        )

    @staticmethod
    def get_target(carousel: Carousel):
        return carousel.url

    @staticmethod
    def get_image(carousel: Carousel):
        return {
            'url': carousel.image.url,
            'placeholder': carousel.image_placeholder,
        }
