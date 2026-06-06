import random
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Question, Answer
from .serializers import (
    CategorySerializer, QuestionSerializer,
    QuestionAdminSerializer, AnswerWithCorrectSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve quiz categories."""
    queryset = Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    @action(detail=False, methods=['get'], url_path='all')
    def all_flat(self, request):
        """All categories including subcategories, flat list."""
        cats = Category.objects.filter(is_active=True)
        return Response(CategorySerializer(cats, many=True).data)


class QuestionViewSet(viewsets.ModelViewSet):
    """Questions — read-only for users, full CRUD for admins."""
    queryset = Question.objects.filter(is_active=True).select_related('category').prefetch_related('answers')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category__slug', 'difficulty']
    search_fields = ['text']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return QuestionAdminSerializer
        return QuestionSerializer

    @action(detail=False, methods=['get'], url_path='random')
    def random_questions(self, request):
        """
        Get random questions.
        Query params: count (default 10), difficulty, category_slug
        """
        count = int(request.query_params.get('count', 10))
        difficulty = request.query_params.get('difficulty')
        category_slug = request.query_params.get('category')

        qs = Question.objects.filter(is_active=True).prefetch_related('answers')
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        count = min(count, qs.count())
        questions = random.sample(list(qs), count)
        return Response(QuestionSerializer(questions, many=True).data)

    @action(detail=False, methods=['get'], url_path='classic-set')
    def classic_set(self, request):
        """
        Return 15 questions in classic Millionaire difficulty progression.
        Easy(5) → Medium(5) → Hard(3) → Expert(2)
        """
        category_slug = request.query_params.get('category')
        qs = Question.objects.filter(is_active=True).prefetch_related('answers')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        def pick(diff, n):
            pool = list(qs.filter(difficulty=diff))
            return random.sample(pool, min(n, len(pool)))

        questions = (
            pick('easy', 5) +
            pick('medium', 5) +
            pick('hard', 3) +
            pick('expert', 2)
        )
        random.shuffle(questions)
        return Response(QuestionSerializer(questions, many=True).data)
