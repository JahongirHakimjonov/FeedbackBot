from django.contrib import admin
from django.db.models import Avg

from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_num', 'type', 'course_num', 'is_active')
    exclude = ('course_num',)
    list_filter = ('is_active', 'type')
    search_fields = ('group_num',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'telegram_id', 'group_number', 'course_num', 'is_active')
    fields = ('login_id', 'password', 'first_name', 'last_name', 'telegram_id', 'group', 'is_active')
    list_filter = ('group', 'is_active', 'course_num')
    search_fields = ('first_name', 'last_name', 'telegram_id')

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = 'Guruh raqami'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'degree', 'average_score', 'percentage', 'is_active')
    list_filter = ('degree', 'is_active',)
    search_fields = ('first_name', 'last_name', 'degree')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "To'liq ism"

    def average_score(self, obj):
        avg_score = Score.objects.filter(teacher=obj).aggregate(avg_score=Avg('score_for_teacher'))['avg_score']
        return avg_score if avg_score is not None else 0

    average_score.short_description = "O'rtacha baho"

    def percentage(self, obj):
        avg_score = Score.objects.filter(teacher=obj).aggregate(avg_score=Avg('score_for_teacher'))['avg_score']
        return avg_score * 20 if avg_score is not None else 0

    percentage.short_description = "Foiz %"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_names', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'teacher__first_name', 'teacher__last_name')

    def teacher_names(self, obj):
        return ", ".join([f"{teacher.first_name} {teacher.last_name}" for teacher in obj.teacher.all()])

    teacher_names.short_description = 'Ustozlar'
    #
    # def average_score(self, obj):
    #     avg_score = Score.objects.filter(lesson=obj).aggregate(avg_score=Avg('score_for_teacher'))['avg_score']
    #     return avg_score if avg_score is not None else 0
    #
    # average_score.short_description = "O'rtacha baho"
    #
    # def percentage(self, obj):
    #     avg_score = Score.objects.filter(lesson=obj).aggregate(avg_score=Avg('score_for_teacher'))['avg_score']
    #     return avg_score * 20 if avg_score is not None else 0
    #
    # percentage.short_description = "Foiz %"


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'lesson_name', 'score_for_teacher', 'feedback')
    list_filter = ('teacher__first_name', 'teacher__last_name', 'lesson__name')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'lesson__name')

    def teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    teacher_name.short_description = 'Ustoz'

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = 'Fan nomi'


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'lesson_name', 'teacher_names', 'group_number', 'start_time')
    exclude = ('end_time',)
    list_filter = ('group', 'day', 'lesson__name')
    search_fields = ('group__group_num', 'lesson__name')

    def teacher_names(self, obj):
        return ", ".join([f"{teacher.first_name} {teacher.last_name}" for teacher in obj.teacher.all()])

    teacher_names.short_description = 'Ustozlar'

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = 'Guruh raqami'

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = 'Fan nomi'
