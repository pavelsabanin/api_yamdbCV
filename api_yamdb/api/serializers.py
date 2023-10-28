from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from reviews.models import Category, Genre, Title, Review, Comment
from django.core.validators import MinValueValidator, MaxValueValidator
User = get_user_model()
from rest_framework.generics import get_object_or_404 

from rest_framework.exceptions import ValidationError

class UserCreationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать me в качестве username')
        return value


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'email',
                  'first_name', 'last_name', 'bio')
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role',
                  'first_name', 'last_name', 'bio')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', many=True,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        required=False
    )
    title = serializers.StringRelatedField(required=False)

    def validate(self, data):
        title_id = self.context['view'].kwargs['title_id']
        author = self.context['request'].user
        if self.context['request'].method == 'POST':
            if Review.objects.filter(title=title_id, author=author.id).exists():
                raise serializers.ValidationError(
                    'Разрешается оставлять отзыв всего один раз.'
                )
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'review': {'required': False},
            'author': {'required': False},
        }

    def create(self, validated_data):
        review_id = self.context['view'].kwargs['review_id']  # Параметр URL с ID отзыва
        if not Review.objects.filter(id=review_id).exists():
            raise serializers.ValidationError('Нет отзыва')
        review = Review.objects.get(id=review_id)
        validated_data['review'] = review
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
