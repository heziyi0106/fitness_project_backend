# Generated by Django 5.1.2 on 2024-10-25 06:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('goal', models.CharField(choices=[('muscle_gain', 'Muscle Gain'), ('fat_loss', 'Fat Loss'), ('endurance', 'Endurance'), ('flexibility', 'Flexibility'), ('general_fitness', 'General Fitness')], default='general_fitness', max_length=20)),
                ('total_duration', models.PositiveIntegerField(default=0, help_text='Total duration in minutes')),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_name', models.CharField(max_length=100)),
                ('body_part', models.CharField(choices=[('chest', 'Chest'), ('back', 'Back'), ('legs', 'Legs'), ('shoulders', 'Shoulders'), ('arms', 'Arms'), ('core', 'Core'), ('full_body', 'Full Body')], default='full_body', max_length=20)),
                ('joint_type', models.CharField(choices=[('single_joint', 'Single Joint'), ('multi_joint', 'Multi Joint')], default='multi_joint', max_length=20)),
                ('sets', models.PositiveIntegerField()),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sets', to='exercise.exercise')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='exercise_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercise.exercisetype'),
        ),
        migrations.CreateModel(
            name='SetDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reps', models.PositiveIntegerField()),
                ('weight', models.FloatField()),
                ('actual_duration', models.PositiveIntegerField(help_text='Actual duration per set in seconds')),
                ('rest_time', models.PositiveIntegerField(help_text='Rest time between sets in seconds')),
                ('exercise_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='exercise.exerciseset')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exercises', models.ManyToManyField(to='exercise.exercise')),
            ],
        ),
    ]
