from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('new', views.new, name='new'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('listings/<path:title>-<int:listing_id>', views.listing, name='listing'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('bids', views.bids, name='bids'),
    path('my-listings', views.myListings, name='my-listings'),
]
