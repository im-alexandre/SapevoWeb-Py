# Generated by Django 2.1 on 2018-11-15 22:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alternativa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Avaliacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternativa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Alternativa')),
            ],
        ),
        migrations.CreateModel(
            name='Criterio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Decisor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Peso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.TextField()),
                ('description', models.TextField()),
                ('valor', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Projeto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
                ('decisores', models.ManyToManyField(related_name='_projeto_decisores_+', to='core.Decisor')),
                ('dono', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Decisor')),
            ],
        ),
        migrations.AddField(
            model_name='criterio',
            name='projeto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Projeto'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='criterio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Criterio'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='decisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Decisor'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='peso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Peso'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='projeto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Projeto'),
        ),
        migrations.AddField(
            model_name='alternativa',
            name='projeto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Projeto'),
        ),
    ]
