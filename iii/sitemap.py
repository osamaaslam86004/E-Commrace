from blog.sitemaps import BlogPostSitemap
from i.sitemaps import MonitorsSitemap


sitemaps = {
    "blog": BlogPostSitemap(),
    "monitors": MonitorsSitemap(),
}
