# Generated by Django 5.1.7 on 2025-03-23 03:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_order_delivery_partner_order_estimated_delivery_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDashboardPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_widgets', models.JSONField(default=list)),
                ('widget_settings', models.JSONField(default=dict)),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('blue', 'Blue'), ('green', 'Green')], default='light', max_length=20)),
                ('layout', models.CharField(choices=[('compact', 'Compact'), ('comfortable', 'Comfortable'), ('spacious', 'Spacious')], default='comfortable', max_length=20)),
                ('show_welcome', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_preference', to='shop.customer')),
            ],
        ),
    ]
