from django.contrib.sitemaps import Sitemap
from i.models import Monitors
from datetime import datetime


class MonitorsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    limit = 10000  # Maximum number of URLs per sitemap file

    def items(self):
        return Monitors.objects.all()

    def lastmod(self, obj):
        return datetime.now()
