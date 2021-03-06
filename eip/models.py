from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from time import strftime

# Create your models here.

def get_pld_path(instance, filename):
    return strftime(f"eip/pld/%Y/%m/%d/2021_PLD_Split_%Y%m{instance.type}.pdf")

class ProjectLogDocument(models.Model):
    """
    """

    PLD_TYPE_CHOICES = [
        ('KO', 'Kick off'),
        ('FU', 'Follow up'),
        ('D', 'Delivery'),
    ]

    type = models.CharField(max_length=2, choices=PLD_TYPE_CHOICES)
    file = models.FileField(upload_to=get_pld_path)
    meeting = models.ForeignKey('Meeting', on_delete=models.SET_NULL, null=True)

    def clean(self):
        if not self.file.name.endswith(".pdf"):
            raise ValidationError("The file must be of pdf type")

    def save(self, *args, **kwargs):
        old = ProjectLogDocument.objects.filter(id=self.id)
        if old.count:
            if old.file != self.file:
                old.file.delete()
        super(ProjectLogDocument, self).save(*args, **kwargs)


class Meeting(models.Model):
    """
    """

    name = models.CharField(max_length=50)
    date = models.DateTimeField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return f"{self.name} on {self.date.strftime('%Y-%m-%d %H:%M')} with {self. members.count()} members"
