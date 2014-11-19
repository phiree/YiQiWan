# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import model_utils.fields
from django.utils.timezone import utc
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(blank=True, null=True, max_length=300)),
                ('description', models.CharField(blank=True, null=True, max_length=8000)),
                ('min_participants', models.IntegerField()),
                ('max_participants', models.IntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('close_time', model_utils.fields.MonitorField(monitor='status', default=django.utils.timezone.now, when=set(['d', 'o', 'C', 'l', 's', 'e']), blank=True, null=True)),
                ('participate_deadline', models.DateTimeField()),
                ('activity_type', models.CharField(blank=True, null=True, max_length=100)),
                ('total_cost_expected', models.IntegerField()),
                ('total_cost_max_expected', models.IntegerField()),
                ('total_cost_actual', models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)),
                ('status', models.CharField(default='Open', blank=True, choices=[('Open', 'Open'), ('Progressing', 'Progressing'), ('Over', 'Over'), ('Closed', 'Closed')], max_length=20)),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Activity_Timeline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('occur_time', models.DateTimeField(default=datetime.datetime(2014, 11, 19, 19, 43, 22, 752629, tzinfo=utc))),
                ('direction', models.CharField(choices=[('L', 'leave'), ('J', 'join')], max_length=10)),
                ('activity', models.ForeignKey(to='web.Activity')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Balance_Flow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('flow_type', models.CharField(choices=[('activity_pre_checkout', '活动预结帐'), ('activity_checkout', '活动结帐'), ('activity_checkout', '活动取消'), ('recharge_offline', '在线充值'), ('withdraw_offline', '在线提现'), ('recharge_online', '离线充值'), ('withdraw_online', '离线提现')], max_length=50)),
                ('amount', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='金额')),
                ('occur_time', models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 19, 19, 43, 22, 758629, tzinfo=utc))),
                ('applied', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Base_Balance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('amount_capital_debt', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='资产/负债')),
                ('amount_profit_loss', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='利润/亏损')),
                ('amount_payables_receivables', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='应收/应付')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Checkout_Strategy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('founder_profit_percent', models.DecimalField(max_digits=2, decimal_places=1, default=0.2)),
                ('is_founder_free', models.BooleanField(default=False)),
                ('last_update_time', models.DateTimeField(auto_now=True, default=datetime.datetime(2014, 11, 19, 19, 43, 22, 759629, tzinfo=utc))),
                ('enabled', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Checkout_Strategy_Fix_Charge',
            fields=[
                ('checkout_strategy_ptr', models.OneToOneField(primary_key=True, to='web.Checkout_Strategy', serialize=False, auto_created=True, parent_link=True)),
                ('fix_charge', models.DecimalField(max_digits=9, decimal_places=1)),
            ],
            options={
            },
            bases=('web.checkout_strategy',),
        ),
        migrations.CreateModel(
            name='Checkout_Strategy_Percent_Charge',
            fields=[
                ('checkout_strategy_ptr', models.OneToOneField(primary_key=True, to='web.Checkout_Strategy', serialize=False, auto_created=True, parent_link=True)),
                ('percent_charge', models.DecimalField(max_digits=3, decimal_places=2)),
                ('max_charge', models.IntegerField()),
            ],
            options={
            },
            bases=('web.checkout_strategy',),
        ),
        migrations.CreateModel(
            name='Financial_Statement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('amount_for_participants', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='参与者支付金额')),
                ('amount_for_founder', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='创建者收取金额')),
                ('amount_for_founder_profit', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='创建者盈利')),
                ('amount_for_system_profit', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='系统盈利')),
                ('status', model_utils.fields.StatusField(verbose_name=(('Pendding', 'Pendding'), ('Complete', 'Complete')), default='Pendding', choices=[('Pendding', 'Pendding'), ('Complete', 'Complete')], no_check_for_status=True, max_length=100)),
                ('occur_time', models.DateTimeField()),
                ('complete_time', models.DateTimeField(null=True)),
                ('activity', models.ForeignKey(to='web.Activity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=300)),
                ('coordinate_x', models.DecimalField(max_digits=9, decimal_places=6)),
                ('coordinate_y', models.DecimalField(max_digits=9, decimal_places=6)),
                ('phone', models.CharField(max_length=200)),
                ('create_date', models.DateTimeField()),
                ('last_update_time', models.DateTimeField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('owner', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('occur_time', models.DateTimeField()),
                ('amount', models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='金额')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User_Balance',
            fields=[
                ('base_balance_ptr', models.OneToOneField(primary_key=True, to='web.Base_Balance', serialize=False, auto_created=True, parent_link=True)),
                ('owner', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('web.base_balance',),
        ),
        migrations.CreateModel(
            name='User_User_Balance',
            fields=[
                ('base_balance_ptr', models.OneToOneField(primary_key=True, to='web.Base_Balance', serialize=False, auto_created=True, parent_link=True)),
                ('other_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user_user_balance_other_user')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user_user_balance_owner')),
            ],
            options={
            },
            bases=('web.base_balance',),
        ),
        migrations.AddField(
            model_name='recharge',
            name='from_balance',
            field=models.ForeignKey(to='web.User_Balance', related_name='recharge_from'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recharge',
            name='to_balance',
            field=models.ForeignKey(to='web.User_Balance', related_name='recharge_to'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balance_flow',
            name='account',
            field=models.ForeignKey(to='web.Base_Balance', related_name='balance_flow_from'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balance_flow',
            name='activity',
            field=models.ForeignKey(blank=True, null=True, to='web.Activity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='checkout_strategy',
            field=models.ForeignKey(to='web.Checkout_Strategy', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='founder',
            field=models.ForeignKey(verbose_name='创建者', blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='activity_founder', help_text='创建者'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='participants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, null=True, related_name='activity_participants'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='place',
            field=models.ForeignKey(to='web.Place'),
            preserve_default=True,
        ),
    ]
