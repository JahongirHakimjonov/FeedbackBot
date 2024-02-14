from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group


class StudentResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, 'group_num'))

    class Meta:
        model = Student
        fields = ('login_id', 'password', 'first_name', 'last_name', 'group', 'course_num')
        exclude = ('id',)
        import_id_fields = ['login_id']


class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('id', 'first_name', 'last_name')

    def get_import_id_fields(self):
        return ['id']


class LessonResource(resources.ModelResource):
    class Meta:
        model = Lesson
        fields = ('id', 'name',)

    def get_import_id_fields(self):
        return ['id']


class ClassScheduleResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, 'group_num'))
    lesson = fields.Field(
        column_name='lesson',
        attribute='lesson',
        widget=ForeignKeyWidget(Lesson, 'name'))
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget(Teacher, 'first_name'))

    class Meta:
        model = ClassSchedule
        fields = ('group', 'lesson', 'teacher', 'day_of_week', 'lesson_time', 'class_room')


class ScoreResource(resources.ModelResource):
    class Meta:
        model = Score
        fields = ('id', 'score_for_teacher', 'feedback', 'teacher__first_name', 'teacher__last_name', 'lesson__name')

    def get_import_id_fields(self):
        return ['id']


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group
        fields = ('id', 'group_num', 'type', 'course_num')

    def get_import_id_fields(self):
        return ['id']
