from .utils import portfolio_details
from .utils import BlogListView, BlogDetailView, BlogCategoryListView, BlogSearchWordListView, BlogTagListView
from .utils import terms, privacy, home
# ============================ Home ===================================
def test_home(request):
    context = {}
    return home(request,'shared_lib/test/_home.html', context)


# =========================== Test ================================
def test_portfolio_details(request, pk):
    return portfolio_details(request, 'shared_lib/_test_portfolio_details.html', pk, {})

def test_terms(request):
    return terms(request, 'shared_lib/test/_test_pricacy.html', {})

def test_privacy(request):
    return privacy(request, 'shared_lib/test/_test_pricacy.html', {} )

class SharedLibBlogListView(BlogListView):
    template_name = "shared_lib/test/_test_blog_list.html"


class SharedLibBlogDetailView(BlogDetailView):
    template_name = "shared_lib/test/_test_blog_detail.html"


class SharedLibBlogCategoryListView(BlogCategoryListView):
    template_name = "shared_lib/test/_test_blog_list.html"


class SharedLibBlogSearchWordListView(BlogSearchWordListView):
    template_name = "shared_lib/test/_test_blog_list.html"


class SharedLibBlogTagListView(BlogTagListView):
    template_name = "shared_lib/test/_test_blog_list.html"




