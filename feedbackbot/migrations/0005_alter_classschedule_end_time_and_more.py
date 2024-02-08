# Generated by Django 5.0.1 on 2024-02-08 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbackbot', '0004_alter_teacher_degree'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classschedule',
            name='end_time',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='classschedule',
            name='start_time',
            field=models.CharField(choices=[('08:30:00', '1-PARA, 08:30'), ('10:00:00', '2-PARA, 10:00'), ('11:30:00', '3-PARA, 11:30'), ('13:00:00', '4-PARA, 13:00'), ('13:30:00', '5-PARA, 13:30'), ('15:00:00', '6-PARA, 15:00'), ('16:30:00', '7-PARA, 16:30')], max_length=15),
        ),
    ]
