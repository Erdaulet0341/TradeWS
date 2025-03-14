# Generated by Django 4.2.20 on 2025-03-11 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TickerAggregate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=10, verbose_name='Торговая пара')),
                ('start_time', models.DateTimeField(db_index=True, verbose_name='Начало интервала')),
                ('end_time', models.DateTimeField(verbose_name='Конец интервала')),
                ('open_price', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Открытие')),
                ('close_price', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Закрытие')),
                ('high_price', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Максимум')),
                ('low_price', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Минимум')),
                ('volume', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Объём')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=10, verbose_name='Торговая пара')),
                ('price', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Цена')),
                ('quantity', models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Объём')),
                ('trade_time', models.DateTimeField(db_index=True, verbose_name='Время сделки')),
            ],
            options={
                'ordering': ['-trade_time'],
            },
        ),
    ]
