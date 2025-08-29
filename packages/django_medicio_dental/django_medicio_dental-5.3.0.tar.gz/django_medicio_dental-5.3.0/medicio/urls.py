from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views

from shared_lib.sitemaps import BlogPostSitemap, PortfolioSitemap
from .sitemaps import StaticViewSitemap

app_name = 'medicio'

sitemaps = {
    "posts": BlogPostSitemap,
    "portfolios": PortfolioSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.medicio_home, name='home'),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap", ),

    path('portfolio_details/<int:pk>/', views.medicio_portfolio_details, name='portfolio_details'),

    path('blog_details/<slug>', views.MedicioBlogDetailView.as_view(), name='blog_details'),

    path('terms_of_use/', views.medicio_terms, name='terms'),
    path('privacy_policy/', views.medicio_privacy, name='privacy'),
]