from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group
from .resources import StudentResource, TeacherResource, LessonResource, ClassScheduleResource, ScoreResource, \
    GroupResource


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = GroupResource
    list_display = ('id', 'group_num', 'type', 'course_num')
    exclude = ('course_num',)
    list_filter = ('is_active', 'type')
    search_fields = ('group_num',)


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('first_name', 'last_name', 'telegram_id', 'group_number', 'course_num')
    fields = ('login_id', 'password', 'first_name', 'last_name', 'telegram_id', 'group')
    list_filter = ('group', 'course_num')
    search_fields = ('first_name', 'last_name', 'telegram_id')

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = 'Guruh raqami'


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ('full_name', 'average_score', 'percentage')
    search_fields = ('first_name', 'last_name')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "To'liq ism"


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = LessonResource
    list_display = ('name', 'teacher_names')
    search_fields = ('name',)

    def teacher_names(self, obj):
        class_schedule_instances = ClassSchedule.objects.filter(lesson=obj)
        teachers_for_lesson = [cs.teacher for cs in class_schedule_instances]
        return ", ".join([f"{teacher.first_name} {teacher.last_name}" for teacher in teachers_for_lesson])

    teacher_names.short_description = 'Ustozlar'


@admin.register(Score)
class ScoreAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ScoreResource
    list_display = ('teacher_name', 'lesson_name', 'score_for_teacher', 'feedback', 'student')
    list_filter = ('teacher__first_name', 'teacher__last_name', 'lesson__name')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'lesson__name')

    def teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    teacher_name.short_description = 'Ustoz'

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = 'Fan nomi'


@admin.register(ClassSchedule)
class ClassScheduleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClassScheduleResource
    list_display = ('day', 'lesson_name', 'teacher_names', 'group_number', 'start_time')
    exclude = ('end_time',)
    list_filter = ('group', 'day', 'lesson__name', 'group__group_num')
    search_fields = ('group__group_num', 'lesson__name')

    def teacher_names(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    teacher_names.short_description = 'Ustozlar'

    def group_number(self, obj):
        return obj.group.group_num

    group_number.short_description = 'Guruh raqami'

    def lesson_name(self, obj):
        return obj.lesson.name

    lesson_name.short_description = 'Fan nomi'
