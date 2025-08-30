from django import template
from django.template.defaultfilters import stringfilter

from _data import shared_lib
from ..models import BlogCategory, BlogPost, PortfolioCategory, Portfolio


register = template.Library()

@register.filter
@stringfilter
def split(string, sep):
    """Return the string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return string.split(sep)


@register.filter
@stringfilter
def underscore_to_hyphen(string):
    """문자열의 _을 -로 변환한다.

    Example usage: {{ value| underscore_to_hyphen }}
    """
    return string.replace('_', '-')


@register.filter
@stringfilter
def add_br(string, num):
    """num 갯수대로 문자열을 분리하고 <br>태그를 삽입한다..

    Example usage: {{ value|add_br:"2" }} -> 문자열을 둘로 나누고 <br>첨가
    """
    quotient = int(len(string)/int(num))
    index = [0]

    for i in range(1, int(num)):
        temp_index = quotient * i
        # 공백이 나오는 곳에서 문자열을 자르기 위해
        while string[temp_index] != ' ':
            temp_index += 1
        index.append(temp_index)

    new_str = ""
    for i in range(int(num)):
        try:
            new_str += string[index[i]:index[i+1]] + "<br>"
        except IndexError:
            # 맨 마지막 문자열의 경우 indexerror 발생하기 때문에
            new_str += string[index[i]:]

    return new_str


# ============================== analytics ============================================
@register.inclusion_tag('shared_lib/analytics.html')
def analytics():
    return shared_lib.analytics


# ============================== adsense ============================================
@register.inclusion_tag('shared_lib/adsense.html')
def adsense():
    return shared_lib.adsense

#templagetags/shared_tags.py
# =============================== modal ==============================================
from ..models import ModalImageOnly, ModalSingleBG, ModalLinkVideo, ModalRotateBG

@register.inclusion_tag(f"shared_lib/modal/_load.html")
def show_modal():
    popup = None
    try:
        # 활성화된 type5에서 하나(제일 처음 것)을 선택함.
        popup = ModalImageOnly.objects.filter(activate__exact=True)[0]
        print(f"Activated {ModalImageOnly.__name__} objects : {popup}")
    except IndexError:
        pass

    try:
        # 활성화된 type4에서 하나(제일 처음 것)을 선택함.
        popup = ModalSingleBG.objects.filter(activate__exact=True)[0]
        print(f"Activated {ModalSingleBG.__name__} objects : {popup}")
    except IndexError:
        pass
    try:
        # 활성화된 type2에서 하나(제일 처음 것)을 선택함.
        popup = ModalLinkVideo.objects.filter(activate__exact=True)[0]
        print(f"Activated {ModalLinkVideo.__name__} objects : {popup}")
    except IndexError:
        pass

    try:
        # 활성화된 type1에서 하나(제일 처음 것)을 선택함.
        popup = ModalRotateBG.objects.filter(activate__exact=True)[0]
        print(f"Activated {ModalRotateBG.__name__} objects : {popup}")
    except IndexError:
        pass

    context = {
        "dont_show_again": "다시보지않기",
        "type": popup.__class__.__name__,
        "popup": popup,
    }
    print("popup context: ", context)
    return context

@register.inclusion_tag("shared_lib/modal/_load_many.html")
def show_modals():
    """
    활성화된 모든 모달을 수집해서 템플릿으로 전달.
    모달 타입 + pk로 고유 uid를 만들어 id/쿠키에 사용.
    """
    items = []
    # 원하는 우선순서(기존 코드 흐름 존중)
    model_order = [ModalImageOnly, ModalSingleBG, ModalLinkVideo, ModalRotateBG]

    for Model in model_order:
        for popup in Model.objects.filter(activate=True).order_by("id"):
            items.append({
                "type": Model.__name__,
                "popup": popup,
                "uid": f"{Model.__name__}_{popup.pk}",
            })

    return {
        "dont_show_again": "다시보지않기",
        "items": items,
    }


# ================================== calendar ====================================
from datetime import datetime, timedelta
from ..models import Calendar, Event

@register.inclusion_tag(f"shared_lib/calendar/_load.html")
def show_calendar():
    try:
        # 활성화된 달력에서 하나(제일 처음 것)을 선택함.
        calendar1 = Calendar.objects.filter(activate__exact=True)[0]
    except IndexError:
        calendar1 = None

    try:
        # 달력의 이벤트 날짜들을 저장함.
        events = Event.objects.filter(calendar__exact=calendar1)
    except IndexError:
        events = None

    print(events)
    context = {
        "dont_show_again": "다시보지않기",
        "calendar": calendar1,
        "events": events,
        "default_date": set_default_date().strftime("%Y-%m-%d"),
    }
    print("calendards context: ", context)
    return context


def set_default_date(date=25) -> datetime:
    """
    full calendar의 defaultDate를 설정하는 함수
    date 인자 이후의 날짜는 다음달을 표시하도록 default day를 다음달로 반환한다.
    """
    today = datetime.today()
    if today.day >= date:
        return today + timedelta(days=7)
    else:
        return today


# ================================== Blog ===================================
import re
from django.template.loader import render_to_string

from ..forms import SearchForm
from taggit.models import Tag


@register.simple_tag
def sidebar(template_name):
    tags = Tag.objects.all()
    categories = BlogCategory.objects.all()
    category = []
    for category_item in categories:
        category.append([category_item.filter, BlogPost.objects.filter(status=1)
                        .filter(category__filter=category_item.filter).count()])

    context = {
        'template_name': template_name,
        'form': SearchForm(),
        'category': category,
        'all_tags': tags,
        'latest': BlogPost.objects.filter(status=1).order_by('-updated_on')[:6],
    }
    return render_to_string(template_name, context)


@register.filter
def add_img_class(value):
    """
    HTML 문자열에서 모든 <img> 태그에 'img-fluid' 클래스를 추가합니다.
    """
    # 이미 class 속성이 있는 경우 처리
    def replace(match):
        img_tag = match.group(0)
        if 'class="' in img_tag:
            # 기존 클래스에 'img-fluid' 추가
            return re.sub(r'class="([^"]+)"', r'class="\1 img-fluid"', img_tag)
        else:
            # 클래스 속성이 없으면 추가
            return img_tag[:-1] + ' class="img-fluid">'
    # <img> 태그를 찾아서 교체
    return re.sub(r'<img[^>]*>', replace, value)

# =============================== Tesrms & Privacy =========================
@register.inclusion_tag("shared_lib/terms_privacy/terms.html")
def terms(company_name, sdate):
    context = {
        "terms": {
            "company_name": company_name,
            "sdate": sdate,
        },
    }
    return context


@register.inclusion_tag("shared_lib/terms_privacy/privacy.html")
def privacy(company_name, sdate, owner, phone, email, position="담당자", assigned_company_name="데미안소프트"):
    context = {
        "privacy": {
            "company_name": company_name,
            "sdate": sdate,
            "assigned_company_name": assigned_company_name,
            "owner": owner,
            "position": position,
            "phone": phone,
            "email": email,

        },
    }
    return context

# =========================== Testing ===================================================
@register.inclusion_tag("shared_lib/test/_portfolio.html")
def test_portfolio(title, subtitle):
    categories = PortfolioCategory.objects.all()
    items = Portfolio.objects.all()
    context = {
        'categories': categories,
        'items': items,
        'title': title,
        'subtitle': subtitle,
    }
    return context

@register.inclusion_tag("shared_lib/test/_recent_blog_posts.html")
def test_recent_blog_posts(title, subtitle, top_n):
    posts = BlogPost.objects.filter(status=1).filter(remarkable=True).order_by('-updated_on')
    context = {
        'title': title,
        'subtitle': subtitle,
        'top_n': posts[:top_n],
    }
    return context
