from django.contrib.gis.geos import Point
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .models import TreeType, TreeStatus, Tree, Planter
from RSRGA_TMS.trees.models import Planter


class TreeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeType
        fields = ['typeid', 'commonname', 'localname', 'scientificname', 'description', 'uses']


class TreeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeStatus
        fields = ['statusid', 'statusname']


class PlanterSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Planter
        fields = ['planterid', 'firstname', 'lastname', 'fullname']

    @staticmethod
    def get_fullname(obj):
        return f"{obj.firstname} {obj.lastname}"


class TreeSerializer(serializers.ModelSerializer):
    # treetype = serializers.CharField(source='treetype.typename')  # Get typename instead of typeid
    commonname = serializers.CharField(source='treetype.commonname')  # Get commonname instead of typeid
    localname = serializers.CharField(source='treetype.localname')  # Get localname instead of typeid
    scientificname = serializers.CharField(source='treetype.scientificname')  # Get scientificname instead of typeid
    statusname = serializers.CharField(source='status.statusname')  # Get statusname instead of statusid
    planter = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Tree
        fields = ['treeid', 'pointname','commonname', 'localname', 'scientificname', 'location', 'latitude', 'longitude', 'status', 'statusname',
                  'dateplanted', 'planterid', 'planter']

        # Custom update method to handle nested fields
        def update(self, instance, validated_data):
            # Handle nested fields separately
            treetype_data = validated_data.pop('treetype', None)
            status_data = validated_data.pop('status', None)
            planter_data = validated_data.pop('planter', None)

            # Update simple fields
            instance.commonname = validated_data.get('commonname', instance.commonname)
            instance.latitude = validated_data.get('latitude', instance.latitude)
            instance.longitude = validated_data.get('longitude', instance.longitude)

            # Update nested fields if provided
            if treetype_data:
                try:
                    instance.treetype = TreeType.objects.get(typename=treetype_data)  # Modify as needed
                except TreeType.DoesNotExist:
                    raise NotFound(f'TreeType with typename "{treetype_data}" not found.')

            if status_data:
                try:
                    instance.status = TreeStatus.objects.get(id=status_data)  # Ensure this matches your input
                except TreeStatus.DoesNotExist:
                    raise NotFound(f'TreeStatus with id "{status_data}" not found.')

            if planter_data:
                try:
                    instance.planter = Planter.objects.get(id=planter_data)  # Ensure this matches your input
                except Planter.DoesNotExist:
                    raise NotFound(f'Planter with id "{planter_data}" not found.')

            instance.save()
            return instance

    @staticmethod
    def get_planter(obj):
        return f"{obj.planterid.firstname} {obj.planterid.lastname}"  # Combine firstname and lastname

    @staticmethod
    def get_latitude(obj):
        return obj.location.y if obj.location else 0.0

    @staticmethod
    def get_longitude(obj):
        return obj.location.x if obj.location else 0.0

    def create(self, validated_data):
        # Convert the location data to a Point object
        longitude = validated_data.pop('longitude', None)
        latitude = validated_data.pop('latitude', None)
        if longitude is not None and latitude is not None:
            validated_data['location'] = Point(longitude, latitude)
        return super().create(validated_data)