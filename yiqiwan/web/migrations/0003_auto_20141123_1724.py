# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import model_utils.fields
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20141122_2012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='balance_flow',
            old_name='account',
            new_name='account_from',
        ),
        migrations.AddField(
            model_name='balance_flow',
            name='account_to',
            field=models.ForeignKey(null=True, blank=True, related_name='balance_flow_to', to='web.Base_Balance'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='activity_timeline',
            name='occur_time',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 23, 9, 24, 39, 743360, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='balance_flow',
            name='occur_time',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 23, 9, 24, 39, 749361, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='checkout_strategy',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 23, 9, 24, 39, 750361, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='financial_statement',
            name='status',
            field=model_utils.fields.StatusField(verbose_name=(('Pendding', 'Pendding'), ('Complete', 'Complete')), no_check_for_status=True, max_length=100, choices=[(0, 'dummy')], default='Pendding'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user_balance',
            name='owner',
            field=models.OneToOneField(to='web.User2'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user_user_balance',
            name='other_user',
            field=models.ForeignKey(to='web.User2', related_name='user_user_balance_other_user'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user_user_balance',
            name='owner',
            field=models.ForeignKey(to='web.User2', related_name='user_user_balance_owner'),
            preserve_default=True,
        ),
    ]
