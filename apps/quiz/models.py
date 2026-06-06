import uuid
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Quiz categories and subcategories."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Emoji or icon class')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def question_count(self):
        return self.questions.filter(is_active=True).count()


class Question(models.Model):
    """Individual quiz question."""

    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_MEDIUM = 'medium'
    DIFFICULTY_HARD = 'hard'
    DIFFICULTY_EXPERT = 'expert'

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY,   'Easy'),
        (DIFFICULTY_MEDIUM, 'Medium'),
        (DIFFICULTY_HARD,   'Hard'),
        (DIFFICULTY_EXPERT, 'Expert'),
    ]

    POINTS_MAP = {
        DIFFICULTY_EASY:   10,
        DIFFICULTY_MEDIUM: 25,
        DIFFICULTY_HARD:   50,
        DIFFICULTY_EXPERT: 100,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_EASY)
    time_limit = models.IntegerField(default=30, help_text='Seconds allowed to answer')
    points_value = models.IntegerField(default=10)
    explanation = models.TextField(blank=True, help_text='Shown after answering')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'accounts.CustomUser', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='questions_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Stats
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'difficulty']

    def __str__(self):
        return f'[{self.difficulty.upper()}] {self.text[:80]}'

    def save(self, *args, **kwargs):
        # Auto-set points based on difficulty if not manually set
        if not self.pk:
            self.points_value = self.POINTS_MAP.get(self.difficulty, 10)
        super().save(*args, **kwargs)

    @property
    def correct_rate(self):
        if self.times_answered == 0:
            return 0.0
        return round((self.times_correct / self.times_answered) * 100, 1)

    @property
    def correct_answer(self):
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    """Possible answers for a question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f'{mark} {self.text[:60]}'
