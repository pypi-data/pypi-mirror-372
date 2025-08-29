# shared_lib_ds

demiansoft 홈페이지 템플릿의 공통라이브러리 모음

## 설치
1. pip를 이용해서 앱 설치
    ```bash
    pip install shared_lib_ds
    ```
2. 프로젝트 settings.py에 앱 등록
   ```python
   import os
   
   INSTALLED_APPS = [
   "jazzmin", # 관리자 페이지 UI
   'django.contrib.admin',
   ...,
   'shared_lib',
   'markdownx', # 블로그 마크다운에디터
   'hitcount', # 블로그 히트카운터
   'taggit', # 블로그 태그관리
   ...
   ]
   
   # 모델에서 이미지 저장을 위해
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
   
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
   # 장고 어드민페이지 커스터마이징
   from _data import shared_lib
   JAZZMIN_SETTINGS = shared_lib.JAZZMIN_SETTINGS
   MARKDOWNX_MARKDOWN_EXTENSIONS = shared_lib.MARKDOWNX_MARKDOWN_EXTENSIONS
   MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = shared_lib.MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS
   MARKDOWNX_UPLOAD_MAX_SIZE = shared_lib.MARKDOWNX_UPLOAD_MAX_SIZE
   MARKDOWNX_UPLOAD_CONTENT_TYPES = shared_lib.MARKDOWNX_UPLOAD_CONTENT_TYPES
   MARKDOWNX_IMAGE_MAX_SIZE = shared_lib.MARKDOWNX_IMAGE_MAX_SIZE
   ```
3. 프로젝트 urls.py에 다음을 추가한다.
    ```python
   from django.urls import path, include
   from shared_lib import utils
   
   urlpatterns = [
   # robots.txt는 반드시 가장 먼저
   path('robots.txt', utils.robots),
   # 기존 URL 패턴들...
   path('markdownx/', include('markdownx.urls')),
   ]
   
   # 개발 환경에서 미디어 파일 서빙
   from django.conf import settings
   from django.conf.urls.static import static
   
   if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
4. 프로젝트에 media/폴더를 생성하고 default_modal.bg.webp를 넣어 모달 기본배경으로 사용한다.
5. 모델 마이그레이션 생성(모달, 캘린더, 포트폴리오, 블로그 모델 설치)
    ```shell
    python manage.py makemigrations shared_lib
    ```
6. 마이그레이션 적용
    ```shell
    python manage.py migrate
    ```
7. _data/shared_lib.py에 데이터 준비

## 사용법
### < robots.txt >
위의 프로젝트 urls.py 내용만 추가하면 사용가능

### < 구글과 네이버 애널리틱스 지원 >
1. 프로젝트 최상위 _/data/shared_lib.py에 데이터 준비

2. 원하는 앱의 template 파일에 다음을 추가
    ```html
    {% load shared_tags %}
    {% analytics %}
    ```

### < 모달창 & 캘린더 띄우기 >
모달창은 총 4가지 타입, 캘린더 1타입이 있음

1. 관리자 페이지에서 타입별 모달창 생성후 활성화
2. 원하는 앱의 template 파일에 다음을 추가
    ```html
    {% load shared_tags %}
    {% show_modal %}
    {% show_calendar %}
    ```

### < 포트폴리오 details 기능 >
1. 앱에 포트폴리오 태그를 생성해서 portfolio_detail에 연결되도록 생성
   ```python
   from django import template
   from shared_lib.models import  PortfolioCategory, Portfolio
   
   register = template.Library()
   
   @register.inclusion_tag("app/portfolio.html")
   def portfolio(title, subtitle):
       categories = PortfolioCategory.objects.all()
       items = Portfolio.objects.all()
       context = {
           'categories': categories,
           'items': items,
           'title': title,
           'subtitle': subtitle,
       }
       return context
   ```
2. 앱의 views.py에 portfolio_detail 뷰함수 래핑
    ```python
    from shared_lib.utils import portfolio_details
    def app_portfolio_details(request, pk):
        return portfolio_details(request, 'app/portfolio_details.html', 'Portfolio Details', pk)
    ```
3. 앱의 urls.py에 portfolio_detail 연결
    ```python
    from django.urls import path
    from . import views
    
    urlpatterns = [
        path('portfolio_details/<int:pk>/', views.app_portfolio_details, name='portfolio_details')
    ]
    ```
4. porfolio_details html 작성

### < 블로그 기능 >
1. 앱에 최근 블로그 보여주기 태그를 생성해서 blog_detail에 연결되도록 생성
    ```python
    from shared_lib.models import BlogPost
    from django import template
    
    register = template.Library()
    
    @register.inclusion_tag("app/recent-blog-posts.html")
    def recent_blog_posts(title, subtitle, top_n):
       posts = BlogPost.objects.filter(status=1).filter(remarkable=True).order_by('-updated_on')
       context = {
           'title': title,
           'subtitle': subtitle,
           'top_n': posts[:top_n],
       }
       return context
    ```
2. 최근 블로그 보여주는 템플릿 html 추가
3. 앱의 views.py에 블로그 뷰클래스 래핑
    ```python
   from shared_lib.utils import BlogListView, BlogDetailView, BlogCategoryListView, BlogSearchWordListView, BlogTagListView
    class AppBlogListView(BlogListView):
        template_name = "app/_test_blog_list.html"
    
    class AppBlogDetailView(BlogDetailView):
        template_name = "app/_test_blog_detail.html"
    
    class AppBlogCategoryListView(BlogCategoryListView):
        template_name = "app/_test_blog_list.html"
    
    class AppBlogSearchWordListView(BlogSearchWordListView):
        template_name = "app/_test_blog_list.html"
    
    class AppBlogTagListView(BlogTagListView):
        template_name = "app/_test_blog_list.html"
    ```
4. 앱의 urls.py에 뷰클래스 연결
    ```python
    from django.urls import path
    from . import views
    
    urlpatterns = [
        path('blog_list/', views.AppBlogListView.as_view(), name='blog_list'),
        path('blog_details/<slug>', views.AppBlogDetailView.as_view(), name='blog_details'),
        path('blog_category/<str:category_filter>', views.AppBlogCategoryListView.as_view(), name='blog_category'),
        path('blog_search_word/', views.AppBlogSearchWordListView.as_view(), name='blog_search_word'),
        path('blog_tag/<str:tag>', views.AppBlogTagListView.as_view(), name='blog_tag'),
    ]
    ```
5. 템플릿에서 markdown 사용하기 세팅
    ```html
    {% load shared_tags %}
    <p>{{ item.formatted_markdown | add_img_class | safe }}</p>
    ```

6. 블로그 템플릿에서 사이드바 사용하기
    ```html
    {% load shared_tags %}
    {% sidebar 'app/_sidebar.html' %}
    ```

### < 블로그, 포트폴리오 사이트맵 지원 >
1. 앱의 urls.py에 다음을 추가한다.
    ```python
    from shared_lib.sitemaps import BlogPostSitemap, PortfolioSitemap
    
    sitemaps = {
    "posts": BlogPostSitemap,
    "portfolios": PortfolioSitemap,
    }
    
    urlpatterns = [
     ...
    ]
    ```

### < terms & privacy 지원>
1. 앱의 views.py에 terms & privacy 뷰함수 래핑
    ```python
    from shared_lib.utils import terms, privacy
    def app_terms(request):
        return terms(request, 'app/terms.html', "회사명", '2024-10-10')
   
    def app_privacy(request):
        return privacy(request, 'app/pricacy.html', "가락삼성치과", 
                   '2024-10-10', '김형진', '02-431-2804', 'hj3415@gmail.com' )
    ```
2. 앱의 urls.py에 terms & privacy 연결
    ```python
    from django.urls import path
    from . import views
    
    urlpatterns = [
        path('terms_of_use/', views.app_terms, name='terms'),
        path('privacy_policy/', views.app_privacy, name='privacy'),
    ]
    ```

### < Appointment Form 뷰함수 지원 >
1. 앱의 views.py home 뷰함수 래핑
    ```python
    from shared_lib.utils import home
    def app_home(request):
        return home(request,'shared_lib/test/_home.html', 'email@email.com', {})
    ```
2. 앱의 urls.py 에 home 연결

### < seo section 지원 >
1. 앱의 index.html 에 seo html inclusion
   ```html
   {% load shared_tags %}
   {% include 'shared_lib/seo.html' with template_name='app_name' %}
   ```

### < 테스트 페이지 접속하려면 >
http://127.0.0.1:8000/shared_lib/ 로 접속하면 shared_lib 기능을 알수있는 테스트 페이지 접속
이를 위해서 프로젝트의 urls.py에 다음을 추가
```python
from django.urls import path, include

urlpatterns = [
    path('shared_lib/', include('shared_lib.urls', namespace='shared_lib')),
    ...
]
```


