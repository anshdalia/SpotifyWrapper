# Generated by Django 5.1.3 on 2024-11-27 04:18

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DuoWrap_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wrap_name', models.CharField(max_length=100)),
                ('time_sent', models.DateTimeField(auto_now_add=True)),
                ('request_accepted', models.BooleanField(default=False)),
                ('request_denied', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SpotifyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('refresh_token', models.CharField(max_length=150)),
                ('access_token', models.CharField(max_length=150)),
                ('expires_in', models.DateTimeField()),
                ('token_type', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wrap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('day', models.DateField(default=datetime.datetime)),
                ('minutes_listened', models.IntegerField()),
                ('top_genre', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('theme', models.CharField(choices=[('default', 'Default'), ('halloween', 'Halloween'), ('christmas', 'Christmas')], default='default', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wraps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-year'],
                'unique_together': {('user', 'year')},
            },
        ),
        migrations.CreateModel(
            name='DuoWrap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=2024)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('top_artists_comparison', models.JSONField(blank=True, default=dict, null=True)),
                ('top_songs_comparison', models.JSONField(blank=True, default=dict, null=True)),
                ('top_genre_comparison', models.JSONField(blank=True, default=dict, null=True)),
                ('minutes_listened_comparison', models.JSONField(blank=True, default=dict, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duo_wrap_user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duo_wrap_user2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user1', 'user2', 'year')},
            },
        ),
        migrations.CreateModel(
            name='TopSong',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('artist', models.CharField(max_length=200)),
                ('rank', models.PositiveIntegerField()),
                ('image_url', models.URLField(blank=True)),
                ('wrap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='top_songs', to='mainApp.wrap')),
            ],
            options={
                'ordering': ['rank'],
                'unique_together': {('wrap', 'rank')},
            },
        ),
        migrations.CreateModel(
            name='TopArtist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('rank', models.PositiveIntegerField()),
                ('image_url', models.URLField(blank=True)),
                ('wrap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='top_artists', to='mainApp.wrap')),
            ],
            options={
                'ordering': ['rank'],
                'unique_together': {('wrap', 'rank')},
            },
        ),
    ]