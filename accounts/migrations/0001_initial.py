# Generated by Django 5.1.2 on 2024-10-29 08:10

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authtoken', '0004_alter_tokenproxy_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpiringToken',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authtoken.token',),
        ),
    ]
