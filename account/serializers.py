from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password_confirmation = serializers.CharField(min_length=8, write_only=True, required=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password', 'password_confirmation')

    def validate(self, attrs):
        print(attrs, '!!!!!!!!!')
        password2 = attrs.pop('password_confirmation')
        if password2 != attrs['password']:
            raise serializers.ValidationError('Password didn\'t match!')

        validate_password(attrs['password'])

        return attrs

    def validate_first_name(self, value):
        if not value.istitle():
            raise serializers.ValidationError(
                'Name must start with uppercase letter!'
            )
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user
        except KeyError:
            raise serializers.ValidationError('Missing password field.')
        except Exception as e:
            raise serializers.ValidationError('Error occurred while creating user.')

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)