# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20141124_0303'),
    ]

    operations = [

        migrations.RenameField(
            model_name='balance_flow',
            old_name='account_from',
            new_name='account',
        ),
        migrations.RemoveField(
            model_name='balance_flow',
            name='account_to',
        )


    ]
