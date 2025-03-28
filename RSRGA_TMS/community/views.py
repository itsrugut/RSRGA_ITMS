from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from RSRGA_TMS.community.forms import FeedbackForm
from RSRGA_TMS.community.models import Event, Feedback


# Create your views here.
@login_required
def community_engagement(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community_engagement')  # Redirect to the same page
    else:
        form = FeedbackForm()

    events = Event.objects.all()
    context = {
        'events': events,
        'form': form,
    }
    return render(request, 'community_engagement/community_engagement.html', context)


def feedback_list_view(request):
    search_query = request.GET.get('search_query', '')
    feedback_list = Feedback.objects.filter(
        Q(name__icontains=search_query) | Q(message__icontains=search_query)
    ).order_by('-timestamp')
    context = {
        'feedback_list': feedback_list,
        'search_query': search_query,
    }
    return render(request, 'feedback/feedback.html', context)