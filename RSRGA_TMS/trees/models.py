from django.contrib.gis.db import models as geomodels  # For geometry fields
from django.db import models
from RSRGA_TMS.users.models import User


# Create your models here.
class Tree(models.Model):
    treeid = models.AutoField(primary_key=True)
    pointname = models.CharField(max_length=20, blank=True)  # New Point Name field
    treetype = models.ForeignKey('TreeType', on_delete=models.CASCADE)
    location = geomodels.PointField()  # Geometry type for location
    status = models.ForeignKey('TreeStatus', on_delete=models.CASCADE)
    dateplanted = models.DateField()
    # planterid = models.ForeignKey('Planter', on_delete=models.CASCADE)

    def __str__(self):
        return self.pointname


class MaintenanceHistory(models.Model):
    tree = models.ForeignKey(Tree, related_name='maintenance_history', on_delete=models.CASCADE)
    date = models.DateField()
    action = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} on {self.date} for {self.tree.pointname}"


class PlantingHole(models.Model):
    holeid = models.AutoField(primary_key=True)
    location = geomodels.PointField()  # Geometry type for location
    status = models.ForeignKey('TreeStatus', on_delete=models.CASCADE)

    def __str__(self):
        return f"Hole {self.holeid}"


class TreeStatus(models.Model):
    statusid = models.AutoField(primary_key=True)
    statusname = models.CharField(max_length=50)

    def __str__(self):
        return self.statusname


class TreeType(models.Model):
    typeid = models.AutoField(primary_key=True)
    commonname = models.CharField(max_length=100)
    localname = models.CharField(max_length=100, null=True, blank=True)
    scientificname = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    uses = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.commonname
