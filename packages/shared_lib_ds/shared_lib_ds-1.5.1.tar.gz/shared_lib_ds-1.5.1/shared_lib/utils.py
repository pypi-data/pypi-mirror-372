from .forms import AppointmentForm
from utils_hj3415 import noti
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

def robots(request):
    robots_contents = """User-agent: *
Disallow: /admin
Allow: /

User-agent: Mediapartners-Google
Allow: /

User-agent: bingbot
Crawl-delay: 30"""
    return HttpResponse(robots_contents, content_type="text/plain")

# ============================ Home ==========================================

def home(request, template_name, context):
    method = request.method.upper()
    if method == "POST":
        context.update(
            make_post_context(
                request.POST,
                context['basic_info']['consult_email'],
                template_name.split('/')[0]
            )
        )
        return render(request, template_name, context)
    else:
        # GET 또는 HEAD
        context.update({
            'form': AppointmentForm(),
            'post_message': None,
        })
        resp = render(request, template_name, context)
        return resp

def make_post_context(request_post, consult_mail, app_name):
    #logger.info(request_post)
    context = {}
    # appointment 앱에서 post 요청을 처리함.
    #logger.info(f'request.POST : {request_post}')
    form = AppointmentForm(request_post)

    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        date = form.cleaned_data['date']
        phone = form.cleaned_data['phone']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        print(f'Pass validation test - name: {name}, email: {email}, date: {date}, phone: {phone}, subject: {subject}, message: {message}')
        text = (f"이름: {name}\n" +
                (f"메일: {email}\n" if email else "") +
                (f"날짜: {date}\n" if date else "") +
                (f"연락처: {phone}\n" if phone else "") +
                (f"제목: {subject}\n" if email else "") +
                f"메시지: {message}\n" +
                f"Message from : {app_name} app")
        print(text)

        is_sendmail = noti.mail_to(title=f'{name} 고객 상담 문의',
                                    text=text,
                                    to_mail=consult_mail)
        if is_sendmail:
            context['post_message'] = '담당자에게  전달되었습니다. 확인 후 바로 연락 드리겠습니다. 감사합니다.'
        else:
            context['post_message'] = '메일 전송에서 오류가 발생하였습니다. 카카오톡이나 전화로 문의주시면 감사하겠습니다. 죄송합니다.'
        return context
    else:
        #logger.error('Fail form validation test')
        context['post_message'] = '입력 항목이 유효하지 않습니다. 다시 입력해 주십시요.'
        return context


# ============================= Portfolio ===================================
from .models import Portfolio


def portfolio_details(request, template_name, pk, context) -> HttpResponse:
    """
    Portfolio Details 페이지 뷰 함수 각 템플릿에서 래핑해서 사용한다.
    :param request:
    :param pk: portfolio model pk
    :param template_name:
    :return:
    """
    context.update({
        "obj": get_object_or_404(Portfolio, pk=pk),
        "breadcrumb": {"title": context['portfolio_title']},
    })
    return render(request, template_name, context)


# =============================== Tesrms & Privacy =========================
def terms(request, template_name, context, title='이용약관'):
    context.update({
        "breadcrumb": {
            "title": title,
        },
        "terms": {
            "company_name": context['basic_info']['company_name'],
            "sdate": context['basic_info']['sdate'],
        },
    })
    return render(request, template_name, context)



def privacy(request, template_name, context, title='개인정보 보호정책',
            position="담당자", assigned_company_name="데미안소프트"):
    context.update({
        "breadcrumb": {
            "title": title,
        },
        "privacy": {
            "company_name": context['basic_info']['company_name'],

            "sdate": context['basic_info']['sdate'],
            "assigned_company_name": assigned_company_name,
            "owner": context['basic_info']['owner'],
            "position": position,
            "phone": context['basic_info']['phone'],
            "email": context['basic_info']['consult_email'],

        },
    })
    return render(request, template_name, context)


# ============================= Blog =====================================
from hitcount.views import HitCountDetailView
from django.views import generic
from .models import BlogPost
from .forms import SearchForm

num_pagination = 6


def make_page_bundle(page_range, n=5):
    # 전체 페이지를 n 개수의 묶음으로 만든다.
    # pagination에 사용
    l = [i for i in page_range]
    return [l[i:i + n] for i in range(0, len(l), n)]


class BlogListView(generic.ListView):
    # 템플릿 이름은 이후에 오버라이드할 예정
    template_name = "shared_lib/test/_test_blog_list.html"
    paginate_by = num_pagination

    def get_queryset(self):
        # https://stackoverflow.com/questions/56067365/how-to-filter-posts-by-tags-using-django-taggit-in-django
        return BlogPost.objects.filter(status=1).order_by('-updated_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages_devided = make_page_bundle(context['paginator'].page_range)

        # 현재 페이지에 해당하는 묶음을 page_bundle로 전달한다.
        for page_bundle in pages_devided:
            if context['page_obj'].number in page_bundle:
                context['page_bundle'] = page_bundle

        context.update({
            "breadcrumb": {"title": "Blog"}
        })
        return context


class BlogCategoryListView(generic.ListView):
    # 템플릿 이름은 이후에 오버라이드할 예정
    template_name = "shared_lib/test/_test_blog_list.html"
    paginate_by = num_pagination

    def get_queryset(self):
        return BlogPost.objects.filter(status=1).filter(category__filter=self.kwargs['category_filter']).order_by('-updated_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages_devided = make_page_bundle(context['paginator'].page_range)

        # 현재 페이지에 해당하는 묶음을 page_bundle로 전달한다.
        for page_bundle in pages_devided:
            if context['page_obj'].number in page_bundle:
                context['page_bundle'] = page_bundle

        context.update({
            "breadcrumb": {"title": "Category: " + self.kwargs['category_filter']}
        })
        return context


class BlogDetailView(HitCountDetailView):
    model = BlogPost
    # 템플릿 이름은 이후에 오버라이드할 예정
    template_name = "shared_lib/test/_test_blog_detail.html"
    context_object_name = 'object'
    slug_field = 'slug'
    count_hit = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #author = get_object_or_404(BlogPost, slug=self.kwargs['slug']).author
        #author = self.kwargs['object'].author
        #print(author.image)

        context.update(
            {'breadcrumb': {'title': 'Blog Detail'}}
        )
        return context


class BlogSearchWordListView(generic.ListView):
    # 템플릿 이름은 이후에 오버라이드할 예정
    template_name = "shared_lib/test/_test_blog_list.html"
    paginate_by = num_pagination

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
        else:
            q = ''
        return BlogPost.objects.filter(content__contains='' if q is None else q).filter(status=1).order_by(
            '-updated_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages_devided = make_page_bundle(context['paginator'].page_range)

        # 현재 페이지에 해당하는 묶음을 page_bundle로 전달한다.
        for page_bundle in pages_devided:
            if context['page_obj'].number in page_bundle:
                context['page_bundle'] = page_bundle

        #print(self.request.GET)
        context.update({
            "breadcrumb": {"title": f"Search : {self.request.GET['q']}"}
        })
        return context


class BlogTagListView(generic.ListView):
    # 템플릿 이름은 이후에 오버라이드할 예정
    template_name = "shared_lib/test/_test_blog_list.html"
    paginate_by = num_pagination

    def get_queryset(self):
        # https://stackoverflow.com/questions/56067365/how-to-filter-posts-by-tags-using-django-taggit-in-django
        return BlogPost.objects.filter(tags__name__in=[self.kwargs['tag']]).filter(status=1).order_by('-updated_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pages_devided = make_page_bundle(context['paginator'].page_range)

        # 현재 페이지에 해당하는 묶음을 page_bundle로 전달한다.
        for page_bundle in pages_devided:
            if context['page_obj'].number in page_bundle:
                context['page_bundle'] = page_bundle

        context.update({
            "breadcrumb": { "title": "Tag: " + self.kwargs['tag']}
        })
        return context

