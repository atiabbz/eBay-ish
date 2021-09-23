from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=128, decimal_places=2, validators=[MinValueValidator(0)])
    imageURL = models.URLField(blank=True)
    category = models.CharField(max_length=128, blank=True, choices=[
        ('fashion', 'Fashion'),
        ('toys', 'Toys'),
        ('electronics', 'Electronics'),
        ('home', 'Home')
    ])
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_listings')
    isActive = models.BooleanField(default=True)
    watchers = models.ManyToManyField(User, blank=True, null=True, related_name='watchlisted_listings')

    def __str__(self):
        return f'{self.creator}: {self.title}'

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.CharField(max_length=256, verbose_name='New comment')
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.commenter}: {self.content[:16]}... '

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=128, decimal_places=2)

    def __str__(self):
        return f'{self.bidder}: {self.listing.title}, ${self.amount}'