from django import forms

from RSRGA_TMS.community.models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Your Name (Optional)',
            'email': 'Your Email (Optional)',
            'message': 'Your Feedback',
        }