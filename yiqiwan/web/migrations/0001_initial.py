# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
from django.utils.timezone import utc
import django.core.validators
import datetime
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0005_alter_user_last_login_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='User2',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', blank=True, verbose_name='groups', related_name='user_set')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission', blank=True, verbose_name='user permissions', related_name='user_set')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=None,
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300, blank=True, null=True)),
                ('description', models.CharField(max_length=8000, blank=True, null=True)),
                ('min_participants', models.IntegerField()),
                ('max_participants', models.IntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('close_time', model_utils.fields.MonitorField(when=set(['o', 'd', 'e', 'C', 'l', 's']), monitor='status', default=django.utils.timezone.now, null=True, blank=True)),
                ('participate_deadline', models.DateTimeField()),
                ('activity_type', models.CharField(max_length=100, blank=True, null=True)),
                ('total_cost_expected', models.IntegerField()),
                ('total_cost_max_expected', models.IntegerField()),
                ('total_cost_actual', models.DecimalField(max_digits=9, blank=True, null=True, decimal_places=1)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Progressing', 'Progressing'), ('Over', 'Over'), ('Closed', 'Closed')], max_length=20, default='Open', blank=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2014, 11, 24, 21, 45, 57, 24498, tzinfo=utc))),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Activity_Timeline',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('occur_time', models.DateTimeField(default=datetime.datetime(2014, 11, 24, 21, 45, 57, 26498, tzinfo=utc))),
                ('direction', models.CharField(choices=[('L', 'leave'), ('J', 'join')], max_length=10)),
                ('activity', models.ForeignKey(to='web.Activity')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Balance_Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('flow_type', models.CharField(choices=[('activity_pre_checkout', '活动预结帐'), ('activity_checkout', '活动结帐'), ('activity_cancel', '活动取消'), ('recharge_offline', '在线充值'), ('withdraw_offline', '在线提现'), ('recharge_online', '离线充值'), ('withdraw_online', '离线提现'), ('activity_return_pre_checkout', '返回预扣款')], max_length=50)),
                ('amount', models.DecimalField(help_text='金额', max_digits=6, default=0, decimal_places=1)),
                ('occur_time', models.DateTimeField(default=datetime.datetime(2014, 11, 24, 21, 45, 57, 29498, tzinfo=utc))),
                ('applied', models.BooleanField(default=False)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Base_Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('amount_capital_debt', models.DecimalField(help_text='资产/负债', max_digits=6, default=0, decimal_places=1)),
                ('amount_profit_loss', models.DecimalField(help_text='利润/亏损', max_digits=6, default=0, decimal_places=1)),
                ('amount_payables_receivables', models.DecimalField(help_text='应收/应付', max_digits=6, default=0, decimal_places=1)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Checkout_Strategy',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('founder_profit_percent', models.DecimalField(max_digits=2, default=0.2, decimal_places=1)),
                ('is_founder_free', models.BooleanField(default=False)),
                ('last_update_time', models.DateTimeField(default=datetime.datetime(2014, 11, 24, 21, 45, 57, 30498, tzinfo=utc))),
                ('enabled', models.BooleanField(default=False)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Financial_Statement',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('amount_for_participants', models.DecimalField(help_text='参与者支付金额', max_digits=6, default=0, decimal_places=1)),
                ('amount_for_founder', models.DecimalField(help_text='创建者收取金额', max_digits=6, default=0, decimal_places=1)),
                ('amount_for_founder_profit', models.DecimalField(help_text='创建者盈利', max_digits=6, default=0, decimal_places=1)),
                ('amount_for_system_profit', models.DecimalField(help_text='系统盈利', max_digits=6, default=0, decimal_places=1)),
                ('status', model_utils.fields.StatusField(choices=[('Pendding', 'Pendding'), ('Complete', 'Complete')], max_length=100, default='Pendding', verbose_name=(('Pendding', 'Pendding'), ('Complete', 'Complete')), no_check_for_status=True)),
                ('occur_time', models.DateTimeField()),
                ('complete_time', models.DateTimeField(null=True)),
                ('activity', models.ForeignKey(to='web.Activity')),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=300)),
                ('coordinate_x', models.DecimalField(max_digits=9, decimal_places=6)),
                ('coordinate_y', models.DecimalField(max_digits=9, decimal_places=6)),
                ('phone', models.CharField(max_length=200)),
                ('create_date', models.DateTimeField()),
                ('last_update_time', models.DateTimeField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Recharge',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('occur_time', models.DateTimeField()),
                ('amount', models.DecimalField(help_text='金额', max_digits=6, default=0, decimal_places=1)),
            ],
            options=None,
            bases=None,
        ),
        migrations.CreateModel(
            name='Checkout_Strategy_Fix_Charge',
            fields=[
                ('checkout_strategy_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='web.Checkout_Strategy', primary_key=True)),
                ('fix_charge', models.DecimalField(max_digits=9, decimal_places=1)),
            ],
            options=None,
            bases=('web.checkout_strategy',),
        ),
        migrations.CreateModel(
            name='Checkout_Strategy_Percent_Charge',
            fields=[
                ('checkout_strategy_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='web.Checkout_Strategy', primary_key=True)),
                ('percent_charge', models.DecimalField(max_digits=3, decimal_places=2)),
                ('max_charge', models.IntegerField()),
            ],
            options=None,
            bases=('web.checkout_strategy',),
        ),
        migrations.CreateModel(
            name='User_Balance',
            fields=[
                ('base_balance_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='web.Base_Balance', primary_key=True)),
                ('owner', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options=None,
            bases=('web.base_balance',),
        ),
        migrations.CreateModel(
            name='User_User_Balance',
            fields=[
                ('base_balance_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='web.Base_Balance', primary_key=True)),
                ('other_user', models.ForeignKey(related_name='user_user_balance_other_user', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(related_name='user_user_balance_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options=None,
            bases=('web.base_balance',),
        ),
        migrations.AddField(
            model_name='balance_flow',
            name='account',
            field=models.ForeignKey(related_name='balance_flow_from', to='web.Base_Balance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='balance_flow',
            name='activity',
            field=models.ForeignKey(to='web.Activity', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='checkout_strategy',
            field=models.ForeignKey(to='web.Checkout_Strategy', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='founder',
            field=models.ForeignKey(help_text='创建者', to=settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name='创建者', related_name='activity_founder'),
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
        migrations.AddField(
            model_name='recharge',
            name='from_balance',
            field=models.ForeignKey(related_name='recharge_from', to='web.User_Balance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recharge',
            name='to_balance',
            field=models.ForeignKey(related_name='recharge_to', to='web.User_Balance'),
            preserve_default=True,
        ),
    ]
