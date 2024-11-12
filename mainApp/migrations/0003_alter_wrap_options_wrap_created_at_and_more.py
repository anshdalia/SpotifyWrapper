# Generated by Django 5.1.1 on 2024-11-12 17:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_alter_wrap_options_alter_topartist_unique_together_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wrap',
            options={'ordering': ['-year']},
        ),
        migrations.AddField(
            model_name='wrap',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='topartist',
            name='image_url',
            field=models.URLField(blank=True, default='/api/placeholder/60/60'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='topartist',
            name='rank',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='topsong',
            name='image_url',
            field=models.URLField(blank=True, default='/api/placeholder/60/60'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='topsong',
            name='rank',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='wrap',
            name='minutes_listened',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wrap',
            name='top_genre',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='wrap',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wraps', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='topartist',
            unique_together={('wrap', 'rank')},
        ),
        migrations.AlterUniqueTogether(
            name='topsong',
            unique_together={('wrap', 'rank')},
        ),
    ]