# Generated by Django 3.1.5 on 2024-02-14 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '0004_remove_author_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('detail', models.TextField(max_length=2000, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/media')),
                ('status', models.CharField(choices=[('商品化', '商品化'), ('保留', '保留')], default='保留', max_length=20)),
                ('email_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('featured', models.BooleanField(default=False)),
                ('visit_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.author')),
            ],
            options={
                'verbose_name_plural': 'Ideas',
            },
        ),
        migrations.CreateModel(
            name='IdeaFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='idea_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('idea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='idea.idea')),
            ],
        ),
        migrations.AddField(
            model_name='idea',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='idea_files', to='idea.IdeaFile'),
        ),
    ]