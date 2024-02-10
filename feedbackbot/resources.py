from import_export import resources, fields
from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('login_id', 'password', 'first_name', 'last_name', 'course_num', 'group__group_num')


class TeacherResource(resources.ModelResource):
    average_score = fields.Field(attribute='average_score', column_name='average_score')
    percentage = fields.Field(attribute='percentage', column_name='percentage')

    class Meta:
        model = Teacher
        fields = ('first_name', 'last_name', 'average_score', 'percentage')


class LessonResource(resources.ModelResource):
    class Meta:
        model = Lesson
        fields = ('name',)


class ClassScheduleResource(resources.ModelResource):
    class Meta:
        model = ClassSchedule
        fields = ('group__group_num', 'lesson__name', 'teacher__first_name', 'teacher__last_name', 'day_of_week',
                  'lesson_time', 'class_room')


class ScoreResource(resources.ModelResource):
    class Meta:
        model = Score
        fields = ('score_for_teacher', 'feedback', 'teacher__first_name', 'teacher__last_name', 'lesson__name')


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group
        fields = ('group_num', 'type', 'course_num')
