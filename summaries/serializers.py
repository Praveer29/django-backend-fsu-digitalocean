# serializers.py
from rest_framework import serializers
from .models import Summary,Feedback
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
#import user model
from django.contrib.auth import get_user_model

User = get_user_model()

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['id', 'youtube_url', 'summary', 'timestamps', 'youtube_transcript', 'date_generated']
        read_only_fields = ['id', 'date_generated']



class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['username', 'email_id', 'feedback']
        
    def create(self, validated_data):
        user = self.context['request'].user if self.context.get('request') else None
        feedback = Feedback.objects.create(
            user=user,
            **validated_data
        )
        return feedback
    
class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=False)
    total_summaries = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 
                 'mobile_number', 'country', 'total_summaries')
        extra_kwargs = {
            'username': {'required': False},
            'mobile_number': {'required': False},
            'country': {'required': False}
        }

    def get_total_summaries(self, obj):
        return obj.summary_set.count()

    def validate(self, attrs):
        # Check if password change is requested
        if 'password' in attrs:
            if 'confirm_password' not in attrs:
                raise serializers.ValidationError(
                    {"confirm_password": "Please confirm your password."}
                )
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."}
                )
            attrs.pop('confirm_password')
        return attrs

    def update(self, instance, validated_data):
        # Handle password separately
        password = validated_data.pop('password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If password was provided, update it
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance