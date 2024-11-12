# Generated by Django 5.1.2 on 2024-11-12 19:06

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
            name='DuoWrap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('top_artists_comparison', models.TextField()),
                ('top_songs_comparison', models.TextField()),
                ('top_genre_comparison', models.TextField()),
                ('minutes_listened_comparison', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wrap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('minutes_listened', models.IntegerField()),
                ('top_genre', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wraps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-year'],
                'unique_together': {('user', 'year')},
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
