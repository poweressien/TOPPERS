from django.contrib import admin
from .models import Category, Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['text', 'is_correct', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'question_count', 'is_active', 'order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'category', 'difficulty', 'points_value', 'times_answered', 'correct_rate', 'is_active']
    list_filter = ['difficulty', 'category', 'is_active']
    search_fields = ['text']
    inlines = [AnswerInline]
    readonly_fields = ['times_answered', 'times_correct', 'correct_rate']

    def text_short(self, obj):
        return obj.text[:70]
    text_short.short_description = 'Question'

    def correct_rate(self, obj):
        return f'{obj.correct_rate}%'
    correct_rate.short_description = 'Correct Rate'
