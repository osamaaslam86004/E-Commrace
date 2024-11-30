from django.contrib.sitemaps import Sitemap
from blog.models import Post


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    limit = 10000  # Maximum number of URLs per sitemap file

    def items(self):
        return Post.objects.filter(status=1)  # Only published posts

    def lastmod(self, obj):
        return obj.modified_on
