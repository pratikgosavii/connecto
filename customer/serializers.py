from rest_framework import serializers
from .models import ScamComplaint, ScamProof

class ScamProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScamProof
        fields = ['id', 'file', 'uploaded_at']


class ScamComplaintSerializer(serializers.ModelSerializer):
    proofs = ScamProofSerializer(many=True, read_only=True)

    class Meta:
        model = ScamComplaint
        fields = '__all__'
        read_only_fields = ['user', 'is_resolved', 'created_at']
