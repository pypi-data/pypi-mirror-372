from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slurpit_netbox', '0025_alter_slurpitprefix_site_rename'),
    ]

    operations = [
        migrations.AddField(
            model_name='slurpitimporteddevice',
            name='os_version',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='slurpitimporteddevice',
            name='serial',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='slurpitimporteddevice',
            name='snmp_uptime',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='slurpitstageddevice',
            name='os_version',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='slurpitstageddevice',
            name='serial',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='slurpitstageddevice',
            name='snmp_uptime',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
