from datetime import datetime, timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_created_at_time(self):
        return self.created_at.strftime('%H:%M')

    def get_updated_at_time(self):
        return self.updated_at.strftime('%H:%M')

    class Meta:
        abstract = True


class Group(AbstractBaseModel):
    TYPE_CHOICES = [
        ('uz', "O'zbek guruh"),
        ('eng', "Ingliz guruh"),
        ('rus', "Rus guruh"),
    ]

    group_num = models.IntegerField(unique=True)
    course_num = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if 101 <= self.group_num <= 115:
            self.course_num = 1
        elif 201 <= self.group_num <= 215:
            self.course_num = 2
        elif 301 <= self.group_num <= 315:
            self.course_num = 3
        elif 401 <= self.group_num <= 415:
            self.course_num = 4
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group_num}"

    class Meta:
        verbose_name_plural = "Guruhlar"
        db_table = "groups"


class Student(AbstractBaseModel):
    login_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')
    course_num = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.course_num = self.group.course_num
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} "

    class Meta:
        verbose_name_plural = "Talabalar"
        db_table = "students"


class Teacher(AbstractBaseModel):
    DEGREE_CHOICES = [
        ('master', 'Magistr'),
        ('bachelor', 'Bakalavr'),
        ('academic', 'Akademik'),
        ('drscience', 'Doktorant'),
        ('phd', 'Professor'),
    ]
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    degree = models.CharField(max_length=10, choices=DEGREE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Uztozlar"
        db_table = "teachers"


class Lesson(AbstractBaseModel):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} "

    class Meta:
        verbose_name_plural = "Fanlar"
        db_table = "lessons"


class Score(AbstractBaseModel):
    score_for_teacher = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} "

    class Meta:
        verbose_name_plural = "Baholar"
        db_table = "scores"


class ClassSchedule(AbstractBaseModel):
    DAYS_OF_WEEK = [
        (0, 'Dushanba'),
        (1, 'Seshanba'),
        (2, 'Chorshanba'),
        (3, 'Payshanba'),
        (4, 'Juma'),
        (5, 'Shanba'),
    ]

    LESSON_START_TIME = [
        ('08:30:00', '1-PARA, 08:30'),
        ('10:00:00', '2-PARA, 10:00'),
        ('11:30:00', '3-PARA, 11:30'),
        ('13:00:00', '4-PARA, 13:00'),
        ('13:30:00', '5-PARA, 13:30'),
        ('15:00:00', '6-PARA, 15:00'),
        ('16:30:00', '7-PARA, 16:30'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.CharField(max_length=15, choices=LESSON_START_TIME)
    end_time = models.CharField(max_length=15, blank=True, null=True)
    room = models.IntegerField()

    def clean(self):
        if self.start_time is None:
            raise ValidationError("Dars boshlanish vaqti kiritilishi shart")

        if self.end_time is None:
            raise ValidationError("Dars tugash vaqti kiritilishi shart")

        if self.start_time >= self.end_time:
            raise ValidationError("Dars tugash vaqti dars boshlanish vaqtidan katta bo'lishi shart")

        if self.day not in dict(self.DAYS_OF_WEEK).keys():
            raise ValidationError("Notog'ri dars kuni kiritildi")

    def save(self, *args, **kwargs):
        start_time_obj = datetime.strptime(self.start_time, '%H:%M:%S')
        end_time_obj = start_time_obj + timedelta(minutes=80)
        self.end_time = end_time_obj.strftime('%H:%M:%S')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group} {self.lesson} {self.teacher} {self.day} {self.start_time} {self.end_time}"

    class Meta:
        verbose_name_plural = "Dars jadvali"
        db_table = "class_schedule"
