# Generated by Django 5.2.3 on 2025-07-07 23:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم النوع')),
            ],
            options={
                'verbose_name': 'نوع تكلفة',
                'verbose_name_plural': 'أنواع التكاليف',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم الأوردر/المشروع')),
                ('start_date', models.DateField(verbose_name='تاريخ البدء')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='تاريخ التسليم المتوقع')),
                ('status', models.CharField(choices=[('جديد', 'جديد'), ('قيد التنفيذ', 'قيد التنفيذ'), ('متوقف', 'متوقف'), ('بانتظار الدفع', 'بانتظار الدفع'), ('مكتمل', 'مكتمل'), ('ملغي', 'ملغي')], default='جديد', max_length=50, verbose_name='الحالة')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.client', verbose_name='العميل')),
            ],
            options={
                'verbose_name': 'مشروع',
                'verbose_name_plural': 'المشاريع',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='تاريخ الدفعة')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='المبلغ المدفوع')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='بيان الدفعة')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='operations.project', verbose_name='المشروع')),
            ],
            options={
                'verbose_name': 'دفعة',
                'verbose_name_plural': 'الدفعات',
            },
        ),
        migrations.CreateModel(
            name='CostItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='التاريخ')),
                ('description', models.CharField(max_length=255, verbose_name='البيان (نوع الخامة أو الخدمة)')),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='الكمية')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='سعر الوحدة')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='operations.costtype', verbose_name='النوع')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cost_items', to='operations.project', verbose_name='المشروع')),
            ],
            options={
                'verbose_name': 'بند تكلفة',
                'verbose_name_plural': 'بنود التكاليف',
            },
        ),
    ]
