from django.shortcuts import render

from RSRGA_TMS.images.models import ArboretumImage, MonthlyDroneCampaign


# Create your views here.
def gallery(request):
    images = ArboretumImage.objects.all()
    context = {
        'images': images
    }
    return render(request, 'gallery/gallery.html', context)


def drone_campaigns(request):
    # Retrieve all campaigns, ordered by the most recent campaign_date
    campaigns = MonthlyDroneCampaign.objects.all().order_by('-campaign_date')
    context = {
        'campaigns': campaigns
    }
    return render(request, 'drone_campaigns/drone_campaigns.html', context)