from django import forms
from .models import Group, Teacher, Lesson, Student, Score, ClassSchedule


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'surname', 'telegram_id', 'group_num', 'courses', 'course_num']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['group_num'].queryset = Group.objects.filter(is_active=True)
    #     self.fields['courses'].queryset = Group.objects.filter(is_active=True)
    #     self.fields['course_num'].queryset = Group.objects.filter(is_active=True)


class BaseCommonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = True


class GroupForm(BaseCommonForm):
    class Meta:
        model = Group
        fields = ['group_num', 'type', 'is_active']


class TeacherForm(BaseCommonForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'is_active']


class LessonForm(BaseCommonForm):
    class Meta:
        model = Lesson
        fields = ['name', 'is_active']


class ScoreForm(BaseCommonForm):
    class Meta:
        model = Score
        fields = ['score_for_teacher', 'feedback', 'teacher', 'lesson', 'student']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
        self.fields['lesson'].queryset = Lesson.objects.filter(is_active=True)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)


class ClassScheduleForm(BaseCommonForm):
    class Meta:
        model = ClassSchedule
        fields = ['group', 'lesson', 'day', 'start_time', 'end_time', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(is_active=True)
        self.fields['lesson'].queryset = Lesson.objects.filter(is_active=True)
