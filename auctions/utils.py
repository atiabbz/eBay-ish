from . import models

def getCategories():
    categories = []
    for category in models.Listing._meta.get_field('category').choices:
        categories.append(category[0])
    return categories