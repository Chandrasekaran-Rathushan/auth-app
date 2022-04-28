# Generated by Django 4.0.2 on 2022-04-28 07:26

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('orderId', models.AutoField(primary_key=True, serialize=False)),
                ('orderNumber', models.TextField(default='ODR-20221', unique=True)),
                ('createdTime', models.DateTimeField(default=datetime.datetime(2022, 4, 28, 7, 25, 59, 472533, tzinfo=utc))),
                ('billingDateTime', models.DateTimeField(default=datetime.datetime(2022, 4, 28, 7, 25, 59, 472533, tzinfo=utc))),
                ('isCreditBill', models.BooleanField(default=False, verbose_name='credit')),
                ('totalItems', models.IntegerField(default=0)),
                ('subTotal', models.FloatField(default=0)),
                ('isOrdered', models.BooleanField(default=False, verbose_name='order status')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('categoryId', models.AutoField(primary_key=True, serialize=False)),
                ('categoryName', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customerId', models.AutoField(primary_key=True, serialize=False)),
                ('customerNumber', models.CharField(default='CUS-20221', max_length=100, unique=True)),
                ('firstName', models.CharField(max_length=255)),
                ('lastName', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('phone1', models.CharField(max_length=255)),
                ('phone2', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('dueAmount', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomIdNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=50)),
                ('prefix', models.CharField(max_length=8)),
                ('isYear', models.BooleanField(default=False)),
                ('suffix', models.CharField(max_length=255)),
                ('idString', models.TextField(default='')),
            ],
            options={
                'verbose_name_plural': 'IdNumbers',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('productId', models.AutoField(primary_key=True, serialize=False)),
                ('productCode', models.CharField(default='ITM-1', max_length=100, unique=True)),
                ('pluCode', models.CharField(max_length=5)),
                ('productName', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('quantity', models.CharField(blank=True, max_length=255, null=True)),
                ('available', models.BooleanField(default=True, verbose_name='available')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='shopping_module.category')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cartItemId', models.AutoField(primary_key=True, serialize=False)),
                ('pricePerUnit', models.FloatField(blank=True, null=True)),
                ('quantity', models.FloatField(default=1)),
                ('price_ht', models.FloatField(blank=True, null=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='shopping_module.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='shopping_module.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='shopping_module.customer'),
        ),
    ]