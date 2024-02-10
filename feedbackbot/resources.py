from import_export import resources
from .models import Student, Teacher, Lesson, ClassSchedule, Score, Group


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'login_id', 'password', 'first_name', 'last_name', 'course_num', 'group__group_num')

    def get_import_id_fields(self):
        return ['id']

    def before_import_row(self, row, **kwargs):
        if 'course_num' in row and row['course_num']:
            row['course_num'] = int(row['course_num'])
        if 'group__group_num' in row and row['group__group_num']:
            group_num = int(row['group__group_num'])
            try:
                group = Group.objects.get(group_num=group_num)
                row['group_id'] = group.id
            except Group.DoesNotExist:
                new_group = Group.objects.create(group_num=group_num, course_num=1, type='default')
                row['group_id'] = new_group.id
        else:
            default_group = Group.objects.first()
            if default_group is not None:
                row['group_id'] = default_group.id
            else:
                new_group = Group.objects.create(group_num=1, course_num=1, type='default')
                row['group_id'] = new_group.id
        if 'group_id' not in row or row['group_id'] is None:
            raise ValueError("group_id cannot be NULL")


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
    class Meta:
        model = ClassSchedule
        fields = ('id', 'group__group_num', 'lesson__name', 'teacher__first_name', 'teacher__last_name', 'day_of_week',
                  'lesson_time', 'class_room')

    def get_import_id_fields(self):
        return ['id']


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
