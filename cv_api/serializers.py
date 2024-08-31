from rest_framework import serializers
from cv_api.models import Education


class EducationListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"

    def update(self, instance, validated_data):
        fields_to_update = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]

        for field in fields_to_update:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
            instance.save()

        return instance