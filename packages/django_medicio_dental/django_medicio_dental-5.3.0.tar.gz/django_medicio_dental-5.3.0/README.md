# django_medicio_dental

demiansoft medicio 템플릿
다른 템플릿과 차이는 진료비 페이지가 있다는것

## 설치
1. pip를 이용해서 앱 설치
    ```bash
    pip install django_medicio_dental
    ```
2. 프로젝트 settings.py에 앱 등록
   ```python
   import os
   
   INSTALLED_APPS = [
   "jazzmin", # 관리자 페이지 UI
   'django.contrib.admin',
   ...,
   'django.contrib.sitemaps',
   'shared_lib',
   'markdownx', # 블로그 마크다운에디터
   'hitcount', # 블로그 히트카운터
   'taggit', # 블로그 태그관리
   ...,
   'medicio',
   ]
   
   # 추가 설정 사항들
   import os
   
   X_FRAME_OPTIONS = 'DENY' # 클릭재킹공격 방지 보안설정
   
   STATICFILES_DIRS = [
       os.path.join(BASE_DIR, '_static/'),
   ]
   
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
   
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
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
    path('admin/', admin.site.urls),
    path('', include('medicio.urls', namespace='medicio')),
    path('shared_lib/', include('shared_lib.urls', namespace='shared_lib')),
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
    python manage.py makemigrations
    ```
6. 마이그레이션 적용
    ```shell
    python manage.py migrate
    ```
7. _data/shared_lib.py 와 _data/medicio.py에 데이터 준비




