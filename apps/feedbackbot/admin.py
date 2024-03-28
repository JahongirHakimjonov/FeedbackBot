from django.contrib import admin
from django.db.models import Avg
from import_export.admin import ImportExportModelAdmin

from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group
from .resources import (
    StudentResource,
    TeacherResource,
    LessonResource,
    ClassScheduleResource,
    ScoreResource,
    GroupResource,
)


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = GroupResource
    list_display = ("group_num", "type", "course_num")
    exclude = ("course_num",)
    list_filter = ("course_num", "type")
    search_fields = ("group_num",)
    date_hierarchy = "created_at"
    list_per_page = 10
    list_max_show_all = 50


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = (
        "first_name",
        "last_name",
        "telegram_id",
        "group_number",
        "course_num",
    )
    fields = ("login_id", "password", "first_name", "last_name", "telegram_id", "group")
    list_filter = ("group", "course_num")
    search_fields = ("first_name", "last_name", "telegram_id", "group__group_num")
    date_hierarchy = "created_at"
    list_max_show_all = 50

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = "Guruh raqami"


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ("full_name", "average_score", "percentage")
    search_fields = ("full_name",)
    date_hierarchy = "created_at"

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def average_score(self, obj):
        avg_score = Score.objects.filter(teacher=obj).aggregate(
            avg_score=Avg("score_for_teacher")
        )["avg_score"]
        return format(avg_score, ".2f") if avg_score is not None else "0.00"

    average_score.short_description = "O'rtacha baho"

    def percentage(self, obj):
        avg_score = Score.objects.filter(teacher=obj).aggregate(
            avg_score=Avg("score_for_teacher")
        )["avg_score"]
        return format(avg_score * 20, ".2f") if avg_score is not None else "0.00"

    percentage.short_description = "Foiz %"

    full_name.short_description = "Ism Familiya"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(average_score=Avg("score__score_for_teacher"))
        return queryset.order_by("average_score")


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = LessonResource
    list_display = ("name",)
    search_fields = ("name",)
    date_hierarchy = "created_at"
    list_per_page = 10
    list_max_show_all = 50

    def teacher_names(self, obj):
        class_schedule_instances = ClassSchedule.objects.filter(lesson=obj)
        teachers_for_lesson = [cs.teacher for cs in class_schedule_instances]
        return ", ".join([f"{teacher.full_name}" for teacher in teachers_for_lesson])

    teacher_names.short_description = "Ustozlar"


@admin.register(Score)
class ScoreAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ScoreResource
    list_display = (
        "teacher_name",
        "lesson_name",
        "score_for_teacher",
        "feedback",
        "student",
    )
    list_filter = ("teacher__full_name", "lesson__name", "student__group")
    search_fields = (
        "teacher__full_name",
        "lesson__name",
        "student__first_name",
        "student__last_name",
    )
    date_hierarchy = "created_at"
    list_max_show_all = 50

    def teacher_name(self, obj):
        return f"{obj.teacher.full_name}"

    teacher_name.short_description = "Ustoz"

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = "Fan nomi"


@admin.register(ClassSchedule)
class ClassScheduleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClassScheduleResource
    list_display = (
        "day",
        "lesson_name",
        "room",
        "teacher_names",
        "group_number",
        "start_time",
    )
    exclude = ("end_time",)
    list_filter = ("group", "day", "lesson__name")
    search_fields = ("group__group_num", "lesson__name")
    date_hierarchy = "created_at"
    list_max_show_all = 50

    def teacher_names(self, obj):
        return f"{obj.teacher.full_name}"

    teacher_names.short_description = "Ustozlar"

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = "Guruh raqami"

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = "Fan nomi"
