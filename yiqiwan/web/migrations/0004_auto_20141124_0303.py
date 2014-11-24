# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20141123_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='System_Balance',
            fields=[
                ('base_balance_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='web.Base_Balance', primary_key=True)),
            ],
            options={
            },
            bases=('web.base_balance',),
        ),
        migrations.AlterField(
            model_name='activity_timeline',
            name='occur_time',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 23, 19, 3, 29, 707073, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balance_flow',
            name='occur_time',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 23, 19, 3, 29, 712074, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='checkout_strategy',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 23, 19, 3, 29, 712074, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='financial_statement',
            name='status',
            field=model_utils.fields.StatusField(no_check_for_status=True, choices=[(0, 'dummy')], max_length=100, default='Pendding', verbose_name=(('Pendding', 'Pendding'), ('Complete', 'Complete'))),
            preserve_default=True,
        ),
    ]
