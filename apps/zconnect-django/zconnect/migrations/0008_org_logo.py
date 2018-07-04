# Generated by Django 2.0.5 on 2018-05-18 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_field_fix_and_editable'),
        ('zconnect', '0007_create_activity_subscription_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogoImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bytes', models.TextField()),
                ('filename', models.CharField(max_length=255)),
                ('mimetype', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationLogo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='zconnect.LogoImage/bytes/filename/mimetype')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('organizations.organization',),
        ),
        migrations.AddField(
            model_name='organizationlogo',
            name='organization',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='logo', to='zconnect.Organization'),
        ),
        migrations.AddField(
            model_name='organizationlogo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organizationlogo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
