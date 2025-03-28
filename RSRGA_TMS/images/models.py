from django.db import models


# Create your models here.
class ArboretumImage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='arboretum_images/')
    date_taken = models.DateTimeField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MonthlyDroneCampaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    campaign_date = models.DateField(help_text="Enter the campaign date (e.g., use the first day of the month).")
    image = models.ImageField(upload_to='monthly_drone_campaign_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-campaign_date']
        verbose_name = "Monthly Drone Campaign"
        verbose_name_plural = "Monthly Drone Campaigns"

    def __str__(self):
        return self.title