from rest_framework import serializers
from .models import GameSession, GameAnswer, UserLifeline, DailyChallenge
from apps.quiz.serializers import QuestionSerializer


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = [
            'id', 'mode', 'category', 'status', 'score',
            'questions_answered', 'correct_answers', 'wrong_answers',
            'current_question_index', 'start_time', 'end_time',
            'time_taken_seconds', 'lifelines_used', 'multiplier',
        ]
        read_only_fields = [
            'id', 'status', 'score', 'questions_answered', 'correct_answers',
            'wrong_answers', 'current_question_index', 'start_time', 'end_time',
            'time_taken_seconds', 'lifelines_used', 'multiplier',
        ]


class GameSessionDetailSerializer(GameSessionSerializer):
    """Session with question data attached."""
    questions = serializers.SerializerMethodField()

    class Meta(GameSessionSerializer.Meta):
        fields = GameSessionSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        from apps.quiz.models import Question
        if not obj.question_ids:
            return []
        questions = Question.objects.filter(id__in=obj.question_ids).prefetch_related('answers')
        # Preserve the stored order
        q_map = {str(q.id): q for q in questions}
        ordered = [q_map[qid] for qid in obj.question_ids if qid in q_map]
        return QuestionSerializer(ordered, many=True).data


class SubmitAnswerSerializer(serializers.Serializer):
    question_id  = serializers.UUIDField()
    answer_id    = serializers.UUIDField(required=False, allow_null=True)
    time_taken   = serializers.IntegerField(min_value=0, default=0)


class UseLifelineSerializer(serializers.Serializer):
    lifeline_type = serializers.ChoiceField(choices=[
        'fifty_fifty', 'phone_friend', 'ask_audience', 'skip', 'second_chance'
    ])
    question_id = serializers.UUIDField()


class GameAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    chosen_answer_text = serializers.CharField(source='chosen_answer.text', read_only=True)

    class Meta:
        model = GameAnswer
        fields = [
            'id', 'question', 'question_text', 'chosen_answer',
            'chosen_answer_text', 'is_correct', 'time_taken_seconds',
            'points_earned', 'answered_at',
        ]


class UserLifelineSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_lifeline_type_display', read_only=True)

    class Meta:
        model = UserLifeline
        fields = ['lifeline_type', 'display_name', 'quantity']


class GameSummarySerializer(serializers.Serializer):
    """Final summary returned when a session completes."""
    session_id = serializers.UUIDField()
    mode = serializers.CharField()
    score = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    accuracy = serializers.FloatField()
    time_taken_seconds = serializers.IntegerField()
    points_awarded = serializers.IntegerField()
    new_total_points = serializers.IntegerField()
    achievements_unlocked = serializers.ListField(child=serializers.DictField(), required=False)
