from rest_framework import serializers
from .models import *



class city_Serializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = ['id', 'name']



class coupon_serializer(serializers.ModelSerializer):
    class Meta:
        model = coupon
        fields = '__all__'




# Step 1: Create a serializer
class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = home_banner
        fields = ['image'] 
    
    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
    


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

