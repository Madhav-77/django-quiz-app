from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

# validates registration of user
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        
        user = User(
            username=validated_data['username'],
            is_active=True
        )
        user.password = make_password(validated_data['password']) # password hashing before saving
        user.save()
        return user

# validates user login
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # check if user exists and password matches
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password): # hashing password entered with db hased password with check_password() 
            # generate token if credentials are valid
            refresh = RefreshToken.for_user(user)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        raise serializers.ValidationError("Invalid credentials")
