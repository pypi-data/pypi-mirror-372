from django.contrib.sitemaps import Sitemap
from .models import BlogPost, Portfolio


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.all().filter(status=1)

    def lastmod(self, obj):
        return obj.updated_on


class PortfolioSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Portfolio.objects.all()

    def lastmod(self, obj):
        return obj.updated_on