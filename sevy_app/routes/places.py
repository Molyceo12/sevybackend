from django.urls import path
from sevy_app.views.places.search import PlaceSearchByTextView, PlaceSearchByCoordinatesView, SavePlaceSelectionView
from sevy_app.views.explore.get_all import GetAllExploreView
from sevy_app.views.explore.search import search_explore

urlpatterns = [
    path('search/text/', PlaceSearchByTextView.as_view(), name='place-search-text'),
    path('search/coordinates/', PlaceSearchByCoordinatesView.as_view(), name='place-search-coordinates'),
    path('search/save/', SavePlaceSelectionView.as_view(), name='place-search-save'),
    path('explore/', GetAllExploreView.as_view(), name='place-explore-all'),
    path('explore/search/', search_explore, name='place-explore-search'),
]
