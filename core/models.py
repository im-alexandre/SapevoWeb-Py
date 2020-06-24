from django.db import models
from django.contrib.postgres.fields import JSONField

class Decisor(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    nome = models.CharField(max_length=20)
    decisores = models.ManyToManyField('Decisor', related_name='+')
    avaliado = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.nome


class Alternativa(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)
    #TODO imagem na alternativa
    # imagem = models.ImageField(upload_to = 'pic_folder/', default = 'pic_folder/no-img.jpg')

    def __str__(self):
        return self.nome


class Criterio(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)
    numerico = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class AvaliacaoCriterios(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    avaliacao = JSONField(default='')

    def __str__(self):
        return '{} - {}'.format(self.decisor, self.criterios)


class AvaliacaoAlternativas(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    criterio = models.ForeignKey('Criterio', on_delete=models.CASCADE)
    avaliacao = JSONField(default='')

    def __str__(self):
        return '{} - {} - {}'.format(self.decisor, self.criterio, self.alternativas)


class PageView(models.Model):
    views = models.IntegerField()
