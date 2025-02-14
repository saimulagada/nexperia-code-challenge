# Generated by Django 5.1.4 on 2025-01-03 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('age', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
            ],
        ),
    ]
