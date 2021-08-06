from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createauction", views.createauction, name="createauction"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("listings/<int:listing_id>/bid", views.placebid, name="bid"),
    path("listings/<int:listing_id>/comment", views.comment, name="comment"),
    path("listings/<int:listing_id>/close", views.closelisting, name="closelisting"),
    path("listings/<int:listing_id>/watch", views.add_to_watchlist, name="addwatch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
]