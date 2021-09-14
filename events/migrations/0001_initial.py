# Generated by Django 3.2.6 on 2021-09-14 19:58

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
                ('message', models.TextField()),
                ('logger', models.TextField(blank=True, null=True)),
                ('level', models.CharField(blank=True, choices=[('debug', 'Debug'), ('info', 'Info'), ('error', 'Error'), ('fatal', 'Fatal'), ('sample', 'Sample'), ('warning', 'Warning')], max_length=8, null=True)),
                ('transaction', models.CharField(blank=True, max_length=128, null=True)),
                ('environment', models.CharField(blank=True, max_length=256, null=True)),
                ('server_name', models.CharField(blank=True, max_length=256, null=True)),
                ('log_message', models.TextField(blank=True, null=True)),
                ('handled', models.BooleanField(default=False)),
                ('mechanism', models.CharField(blank=True, max_length=32, null=True)),
                ('exception_message', models.TextField(blank=True, null=True)),
                ('runtime_name', models.CharField(blank=True, max_length=64, null=True)),
                ('runtime_version', models.CharField(blank=True, max_length=64, null=True)),
                ('runtime_build', models.TextField(blank=True, null=True)),
                ('resolved', models.BooleanField(default=False)),
                ('data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
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
