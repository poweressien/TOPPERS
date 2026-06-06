from rest_framework import serializers
from .models import Category, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'order']  # is_correct is hidden during game


class AnswerWithCorrectSerializer(serializers.ModelSerializer):
    """Includes correct flag — used AFTER answering."""
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    question_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'subcategories', 'question_count', 'order']

    def get_subcategories(self, obj):
        subs = obj.subcategories.filter(is_active=True)
        return CategorySerializer(subs, many=True).data


class CategoryLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


class QuestionSerializer(serializers.ModelSerializer):
    """Question with answers (no is_correct — for active gameplay)."""
    answers = AnswerSerializer(many=True, read_only=True)
    category = CategoryLightSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'category', 'text', 'difficulty', 'time_limit', 'points_value', 'answers']


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Full question serializer for admin/creation."""
    answers = AnswerWithCorrectSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'category', 'text', 'difficulty', 'time_limit', 'points_value',
                  'explanation', 'is_active', 'answers', 'times_answered', 'correct_rate']
        read_only_fields = ['times_answered', 'correct_rate']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for ans in answers_data:
            Answer.objects.create(question=question, **ans)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if answers_data is not None:
            instance.answers.all().delete()
            for ans in answers_data:
                Answer.objects.create(question=instance, **ans)
        return instance
