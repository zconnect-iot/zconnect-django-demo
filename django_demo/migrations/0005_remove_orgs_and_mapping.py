# Generated by Django 2.0.5 on 2018-06-12 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zconnect', '0011_fix_url_length'),
        ('zc_billing', '0002_add_bill_foreign_keys'),
        ('zc_timeseries', '0001_initial'),
        ('organizations', '0003_field_fix_and_editable'),
        ('django_demo', '0004_org_device_related_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companygroup',
            name='distributor',
        ),
        migrations.RemoveField(
            model_name='companygroup',
            name='location',
        ),
        migrations.RemoveField(
            model_name='companygroup',
            name='organization_ptr',
        ),
        migrations.RemoveField(
            model_name='companygroup',
            name='wiring_mapping',
        ),
        migrations.RemoveField(
            model_name='demoproduct',
            name='product_ptr',
        ),
        migrations.RemoveField(
            model_name='demoproduct',
            name='wiring_mapping',
        ),
        migrations.RemoveField(
            model_name='distributorgroup',
            name='location',
        ),
        migrations.RemoveField(
            model_name='distributorgroup',
            name='organization_ptr',
        ),
        migrations.RemoveField(
            model_name='distributorgroup',
            name='wiring_mapping',
        ),
        migrations.RemoveField(
            model_name='mapping',
            name='mapping',
        ),
        migrations.RemoveField(
            model_name='sitegroup',
            name='company',
        ),
        migrations.RemoveField(
            model_name='sitegroup',
            name='location',
        ),
        migrations.RemoveField(
            model_name='sitegroup',
            name='organization_ptr',
        ),
        migrations.RemoveField(
            model_name='sitegroup',
            name='wiring_mapping',
        ),
        migrations.RemoveField(
            model_name='tsrawdata',
            name='device',
        ),
        migrations.RemoveField(
            model_name='demodevice',
            name='email_company_emergency_close',
        ),
        migrations.RemoveField(
            model_name='demodevice',
            name='email_distributor_emergency_close',
        ),
        migrations.RemoveField(
            model_name='demodevice',
            name='email_site_emergency_close',
        ),
        migrations.RemoveField(
            model_name='demodevice',
            name='wiring_mapping',
        ),
        migrations.DeleteModel(
            name='CompanyGroup',
        ),
        migrations.DeleteModel(
            name='DemoProduct',
        ),
        migrations.DeleteModel(
            name='DistributorGroup',
        ),
        migrations.DeleteModel(
            name='Mapping',
        ),
        migrations.DeleteModel(
            name='SiteGroup',
        ),
        migrations.DeleteModel(
            name='TSRawData',
        ),
        migrations.DeleteModel(
            name='WiringMapping',
        ),
    ]
