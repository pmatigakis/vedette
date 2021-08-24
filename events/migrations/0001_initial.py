# Generated by Django 3.2.6 on 2021-08-24 14:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('platform', models.CharField(choices=[('python', 'Python')], max_length=32)),
                ('data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['project_id'], name='ix__event__project_id__project'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['timestamp'], name='ix__event__timestamp'),
        ),
    ]