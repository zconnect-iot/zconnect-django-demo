# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-04 14:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import zconnect._models.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('zc_billing', '0001_initial'),
        ('organizations', '0002_model_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyGroup',
            fields=[
                ('organization_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organizations.Organization')),
            ],
            options={
                'ordering': ['location'],
            },
            bases=('zc_billing.billedorganization',),
        ),
        migrations.CreateModel(
            name='DistributorGroup',
            fields=[
                ('organization_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organizations.Organization')),
            ],
            options={
                'ordering': ['location'],
            },
            bases=('zc_billing.billedorganization',),
        ),
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sensor_key', models.CharField(max_length=50)),
                ('transform_function', models.CharField(blank=True, max_length=50)),
                ('input_key', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DemoDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('online', models.BooleanField(default=False)),
                ('fw_version', models.CharField(blank=True, max_length=50)),
                ('sim_number', models.CharField(blank=True, max_length=25)),
                ('email_site_emergency_close', models.BooleanField(default=False)),
                ('email_company_emergency_close', models.BooleanField(default=False)),
                ('email_distributor_emergency_close', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['product'],
                'default_permissions': ['view', 'change', 'add', 'delete'],
            },
            bases=(zconnect._models.mixins.EventDefinitionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SiteGroup',
            fields=[
                ('organization_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organizations.Organization')),
                ('r_number', models.CharField(max_length=50)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sites', to='django_demo.CompanyGroup')),
            ],
            options={
                'ordering': ['location'],
            },
            bases=('zc_billing.billedorganization',),
        ),
        migrations.CreateModel(
            name='TSRawData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField()),
                ('raw_data', models.CharField(max_length=500)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ts_raw_data', to=settings.ZCONNECT_DEVICE_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WiringMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
