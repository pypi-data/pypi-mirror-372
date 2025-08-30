from django.urls import path
from . import views

app_name = 'shared_lib'

urlpatterns = [
    # 전부 테스트용 연결임.
    path('', views.test_home, name='home'),
    path('portfolio_details/<int:pk>/', views.test_portfolio_details, name='portfolio_details'),

    path('blog_list/', views.SharedLibBlogListView.as_view(), name='blog_list'),
    path('blog_details/<slug>', views.SharedLibBlogDetailView.as_view(), name='blog_details'),
    path('blog_category/<str:category_filter>', views.SharedLibBlogCategoryListView.as_view(), name='blog_category'),
    path('blog_search_word/', views.SharedLibBlogSearchWordListView.as_view(), name='blog_search_word'),
    path('blog_tag/<str:tag>', views.SharedLibBlogTagListView.as_view(), name='blog_tag'),

    path('terms_of_use/', views.test_terms, name='terms'),
    path('privacy_policy/', views.test_privacy, name='privacy'),
]
