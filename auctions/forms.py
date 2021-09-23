from . import models
from django.forms import ModelForm

class NewListingForm(ModelForm):
    class Meta:
        model = models.Listing
        fields = ['title', 'description', 'price', 'imageURL', 'category']

class NewCommentForm(ModelForm):
    class Meta:
        model = models.Comment
        fields = ['content']

class NewBidForm(ModelForm):
    class Meta:
        model = models.Bid
        fields = ['amount']