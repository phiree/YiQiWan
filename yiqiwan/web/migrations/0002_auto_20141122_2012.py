# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import model_utils.fields
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User2',
            fields=[
                ('user', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, primary_key=True)),
            ],
            options={
                'verbose_name': 'user',
                'abstract': False,
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.AlterField(
            model_name='activity',
            name='checkout_strategy',
            field=models.ForeignKey(null=True, to='web.Checkout_Strategy', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='activity',
            name='participants',
            field=models.ManyToManyField(null=True, related_name='activity_participants', to='web.User2', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='activity_timeline',
            name='occur_time',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 22, 12, 12, 48, 396429, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balance_flow',
            name='occur_time',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 22, 12, 12, 48, 402430, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='checkout_strategy',
            name='last_update_time',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 22, 12, 12, 48, 403430, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='financial_statement',
            name='status',
            field=model_utils.fields.StatusField(max_length=100, default='Pendding', choices=[(0, 'dummy')], no_check_for_status=True, verbose_name=(('Pendding', 'Pendding'), ('Complete', 'Complete'))),
            preserve_default=True,
        ),
    ]
