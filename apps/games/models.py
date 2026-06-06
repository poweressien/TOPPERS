import uuid
from django.db import models
from django.conf import settings


class GameSession(models.Model):
    """One complete game session for any game mode."""

    MODE_CLASSIC  = 'classic'
    MODE_DAILY    = 'daily'
    MODE_SURVIVAL = 'survival'
    MODE_SPEED    = 'speed'

    MODE_CHOICES = [
        (MODE_CLASSIC,  'Classic Mode'),
        (MODE_DAILY,    'Daily Challenge'),
        (MODE_SURVIVAL, 'Survival Mode'),
        (MODE_SPEED,    'Speed Mode'),
    ]

    STATUS_ACTIVE     = 'active'
    STATUS_COMPLETED  = 'completed'
    STATUS_ABANDONED  = 'abandoned'

    STATUS_CHOICES = [
        (STATUS_ACTIVE,    'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ABANDONED, 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='game_sessions')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    category = models.ForeignKey(
        'quiz.Category', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sessions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Score
    score = models.IntegerField(default=0)
    questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    current_question_index = models.IntegerField(default=0)

    # Timing
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True)

    # Lifelines & Multiplier
    lifelines_used = models.JSONField(default=list)
    multiplier = models.FloatField(default=1.0)

    # Stored question IDs for this session (ordered list of UUIDs)
    question_ids = models.JSONField(default=list)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.user.username} – {self.mode} – {self.status}'

    def complete(self):
        from django.utils import timezone
        self.status = self.STATUS_COMPLETED
        self.end_time = timezone.now()
        elapsed = (self.end_time - self.start_time).seconds
        self.time_taken_seconds = elapsed
        self.save()


class GameAnswer(models.Model):
    """A single question answer within a game session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('quiz.Question', on_delete=models.CASCADE)
    chosen_answer = models.ForeignKey(
        'quiz.Answer', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='game_answers'
    )
    is_correct = models.BooleanField(default=False)
    time_taken_seconds = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    used_second_chance = models.BooleanField(default=False)

    class Meta:
        ordering = ['answered_at']
        unique_together = ('session', 'question')

    def __str__(self):
        result = '✓' if self.is_correct else '✗'
        return f'{result} {self.question.text[:50]}'


class UserLifeline(models.Model):
    """Tracks how many lifelines a user has available."""

    LIFELINE_FIFTY_FIFTY   = 'fifty_fifty'
    LIFELINE_PHONE_FRIEND  = 'phone_friend'
    LIFELINE_ASK_AUDIENCE  = 'ask_audience'
    LIFELINE_SKIP          = 'skip'
    LIFELINE_SECOND_CHANCE = 'second_chance'

    LIFELINE_CHOICES = [
        (LIFELINE_FIFTY_FIFTY,   '50:50'),
        (LIFELINE_PHONE_FRIEND,  'Phone a Friend'),
        (LIFELINE_ASK_AUDIENCE,  'Ask the Audience'),
        (LIFELINE_SKIP,          'Skip Question'),
        (LIFELINE_SECOND_CHANCE, 'Second Chance'),
    ]

    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='lifelines')
    lifeline_type = models.CharField(max_length=20, choices=LIFELINE_CHOICES)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'lifeline_type')

    def __str__(self):
        return f'{self.user.username} – {self.get_lifeline_type_display()} x{self.quantity}'


class DailyChallenge(models.Model):
    """Daily challenge record — tracks a user's daily streak and participation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='daily_challenges')
    date = models.DateField()
    session = models.OneToOneField(GameSession, on_delete=models.CASCADE, null=True, blank=True)
    bonus_awarded = models.BooleanField(default=False)
    streak_at_time = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} – {self.date}'
