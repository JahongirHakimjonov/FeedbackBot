from datetime import datetime, timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_created_at_time(self):
        return self.created_at.strftime("%H:%M:%S")

    def get_updated_at_time(self):
        return self.updated_at.strftime("%H:%M:%S")

    class Meta:
        abstract = True


class Group(AbstractBaseModel):
    TYPE_CHOICES = [
        ("uz", "O'zbek guruh"),
        ("eng", "Ingliz guruh"),
        ("rus", "Rus guruh"),
    ]

    group_num = models.IntegerField()
    course_num = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if 101 <= self.group_num <= 150:
            self.course_num = 1
        elif 201 <= self.group_num <= 250:
            self.course_num = 2
        elif 301 <= self.group_num <= 350:
            self.course_num = 3
        elif 401 <= self.group_num <= 450:
            self.course_num = 4
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.group_num)

    class Meta:
        verbose_name_plural = "Guruhlar"
        db_table = "groups"


class Student(AbstractBaseModel):
    id = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    course_num = models.IntegerField()
    is_active = models.BooleanField(default=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.course_num = self.group.course_num
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Talabalar"
        db_table = "students"


class Teacher(AbstractBaseModel):
    full_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name}"

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
    score_for_teacher = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
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
        (1, "Dushanba"),
        (2, "Seshanba"),
        (3, "Chorshanba"),
        (4, "Payshanba"),
        (5, "Juma"),
        (6, "Shanba"),
    ]

    LESSON_START_TIME = [
        ("08:30:00", "1-PARA, 08:30"),
        ("09:30:00", "2-PARA, 09:30"),
        ("10:30:00", "3-PARA, 10:30"),
        ("11:30:00", "4-PARA, 11:30"),
        ("12:30:00", "5-PARA, 12:30"),
        ("13:30:00", "6-PARA, 13:30"),
        ("14:30:00", "7-PARA, 14:30"),
        ("15:30:00", "8-PARA, 15:30"),
        ("16:30:00", "9-PARA, 16:30"),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.CharField(max_length=15, choices=LESSON_START_TIME)
    end_time = models.CharField(max_length=15, blank=True, null=True)
    room = models.CharField(max_length=25, blank=True, null=True)

    def save(self, *args, **kwargs):
        if isinstance(self.start_time, str):
            start_time_obj = datetime.strptime(self.start_time, "%H:%M:%S").time()
        else:
            start_time_obj = self.start_time

        end_time_obj = (
            datetime.combine(datetime.today(), start_time_obj) + timedelta(minutes=50)
        ).time()
        self.end_time = end_time_obj.strftime("%H:%M:%S")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group} {self.lesson} {self.teacher} {self.day} {self.start_time} {self.end_time}"

    class Meta:
        verbose_name_plural = "Dars jadvali"
        db_table = "class_schedule"
