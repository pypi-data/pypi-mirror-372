from django.db import models


# ====================================== Modal =========================================
class ModalSingleBG(models.Model):
    modal_title = models.CharField('modal_title', default="EVENT", max_length=50, blank=True)
    h3 = models.CharField('h3', max_length=50, help_text="강조 : strong tag")
    h1 = models.CharField('h1', max_length=100)
    h2 = models.TextField('h2', help_text="줄넘기기 : br tag, 강조 : strong tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    bg = models.ImageField(upload_to=f'images/popup/modal_single_bg',
                           default='default_modal_bg.webp')
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.h1

class ModalImageOnly(models.Model):
    modal_title = models.CharField('modal_title', default="NOTI", max_length=50, blank=True)
    img = models.ImageField(upload_to=f'images/popup/modal_image_only')
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.modal_title

class ModalLinkVideo(models.Model):
    modal_title = models.CharField('modal_title', default="EVENT", max_length=50, blank=True)
    h2 = models.CharField('h2', max_length=100)
    p = models.TextField('p', help_text="줄넘기기 : br tag, 강조 : strong tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    link_video_url = models.CharField('link_video_url', blank=True, help_text="공란 가능", max_length=1200)
    link_video_text = models.CharField('link_video_text', default="Watch Video", max_length=50)
    bg = models.ImageField(upload_to=f'images/popup/modal_link_video',
                           default='default_modal_bg.webp')
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.h2


class ModalRotateBG(models.Model):
    modal_title = models.CharField('modal_title', default="EVENT", max_length=50, blank=True)
    h2 = models.CharField('h2', max_length=100, help_text="줄넘기기 : br tag, 강조 : span tag")
    p = models.TextField('p', help_text="줄넘기기 : br tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    bg = models.ImageField(upload_to=f'images/popup/modal_rotate_bg',
                           default='default_modal_bg.webp')
    bg2 = models.ImageField(blank=True, upload_to=f'images/popup/modal_rotate_bg')
    bg3 = models.ImageField(blank=True, upload_to=f'images/popup/modal_rotate_bg')
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.h2



# =============================== Calendar =============================================


# EventType model: 이벤트 종류 및 색상 정의
class EventType(models.Model):
    """이벤트 종류 및 색상 정의"""
    name = models.CharField('event_type', max_length=20, unique=True)
    color = models.CharField('color', max_length=7, default='#3788d8',
                             help_text="HEX 코드 형식 예: #FF0000")

    def __str__(self):
        return self.name


class Calendar(models.Model):
    modal_title = models.CharField('calendar_name', default="휴진안내", help_text=r"줄넘기기 : \n", max_length=40)
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    def __str__(self):
        return self.modal_title


class Event(models.Model):
    title = models.CharField('title', default="휴진", max_length=20)
    date_of_event = models.DateField()
    calendar = models.ForeignKey(
        'Calendar',
        related_name='calendar',
        on_delete=models.PROTECT,
    )
    event_type = models.ForeignKey(
        'EventType',
        related_name='events',
        on_delete=models.PROTECT,
        null=True,  # ← 일단 null 허용
        blank=True,
    )

    def __str__(self):
        return str(self.title) + '/' + str(self.date_of_event)


# ============================ Portfolio =========================================


class PortfolioCategory(models.Model):
    filter = models.CharField('포트폴리오 카테고리', max_length=20)

    def __str__(self):
        return self.filter


class Portfolio(models.Model):
    title = models.CharField('제목', max_length=50)
    subtitle = models.CharField('부제목', max_length=100)
    filter = models.ForeignKey(PortfolioCategory, related_name='portfolio_category', on_delete=models.PROTECT)
    description = models.TextField('세부 설명', null=True, blank=True)
    image1 = models.ImageField(upload_to=f'images/portfolio/', null=True,
                               help_text="각 이미지 비율이(3x5) 동일한 것이 보기 좋습니다.")
    image2 = models.ImageField(upload_to=f'images/portfolio/', null=True, blank=True)
    image3 = models.ImageField(upload_to=f'images/portfolio/', null=True, blank=True)
    image4 = models.ImageField(upload_to=f'images/portfolio/', null=True, blank=True)
    image5 = models.ImageField(upload_to=f'images/portfolio/', null=True, blank=True)
    client = models.CharField('Client', max_length=20, blank=True)
    reg_time = models.DateTimeField(auto_now_add=True)
    url = models.URLField('참고링크', blank=True, null=True, help_text="공란 가능", max_length=500)

    def __str__(self):
        return self.title


# ================================ Blog ===========================================
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from hitcount.models import HitCount
from taggit.managers import TaggableManager
from django.utils.text import slugify



STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Delete profile when user is deleted
    image = models.ImageField(default='default_profile.jpg', upload_to='profile_pics')
    name = models.CharField('name', default='default', max_length=40)
    desc = models.TextField('desc', null=True, blank=True)
    sns = models.URLField('sns', blank=True, null=True, help_text="공란 가능", max_length=500)

    def __str__(self):
        return f'{self.user.username} Profile'  # show how we want it to be displayed


class BlogCategory(models.Model):
    filter = models.CharField('블로그 카테고리', max_length=20)

    def __str__(self):
        return self.filter


class BlogPost(models.Model):
    title = models.CharField(max_length=200, unique=False)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails', default='default_thumbnail.jpg')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blog_author')
    content = MarkdownxField()
    status = models.IntegerField(choices=STATUS, default=0)
    remarkable = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(BlogCategory, related_name='blog_category', on_delete=models.PROTECT)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    tags = TaggableManager()

    # Create a property that returns the markdown
    @property
    def formatted_markdown(self):
        return markdownify(self.content)

    def save(self, *args, **kwargs):
        # 슬러그가 없을 경우 제목을 기반으로 자동 생성
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title
