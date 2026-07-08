from rest_framework import serializers
from sevy_app.models import Explore, ExploreCategory

class ExploreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExploreCategory
        fields = '__all__'

class ExploreSerializer(serializers.ModelSerializer):
    category = ExploreCategorySerializer(read_only=True)

    class Meta:
        model = Explore
        fields = '__all__'
