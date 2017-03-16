from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class WebSite(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField(editable=False) # Convierte url en url's validas, segun devcode esto hace que el administrador no pueda modificar el name
    url = models.URLField()
    description = models.CharField(max_length=100)
    designer = models.CharField(max_length=100)
    designer_url = models.URLField()
    twitter = models.CharField(max_length=100)
    image1 = models.ImageField(upload_to="websites")   #upload_to significa que va a esa carpeta
    image2 = models.ImageField(upload_to="websites")
    image3 = models.ImageField(upload_to="websites", null=True, blank=True) # con null y blank haces que el campo sea opcional

    create_at = models.DateTimeField(auto_now_add=True) # Fecha de Cuando se creo
    updated_at = models.DateTimeField(auto_now=True) # Fecha de cuando se modifico

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(WebSite, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Vote(models.Model):

    user = models.ForeignKey(User)
    website = models.ForeignKey(WebSite)
    desing = models.IntegerField()
    usability = models.IntegerField()
    creativity = models.IntegerField()
    content = models.IntegerField()

    def __str__(self):
        return "%s - %s" % (self.user.username, self.website.name)  # con esta funcion puedes cambiar el nombre del objeto como se muesta en el panel de administrador
