from django.contrib.staticfiles import finders
import os
from shared_lib.models import BlogPost, PortfolioCategory, Portfolio
from django import template

register = template.Library()

@register.inclusion_tag('medicio/components/gallery.html', takes_context=True)
def gallery(context):
    # static 파일 경로 찾는 방법
    # https://stackoverflow.com/questions/30430131/get-the-file-path-for-a-static-file-in-django-code
    dir = finders.find('medicio/img/gallery')
    #logger.info(f'gallery path: {dir}')

    files = []

    # static 갤러리 폴더안의 사진 파일의 수를 세어서 파일명을 리스트로 만든다.
    # https://www.delftstack.com/howto/python/count-the-number-of-files-in-a-directory-in-python/
    # https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
    if dir:
        for file in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, file)) and file.endswith('.jpg'):
                files.append(file)
       # logger.info(files)

    context.update({
        'gallery_files': files
    })
    #logger.info(context)
    return context

@register.inclusion_tag("medicio/components/portfolio.html")
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


@register.inclusion_tag("medicio/footer.html", takes_context=True)
def footer(context):
    context.update({
        'remarkables': BlogPost.objects.filter(status=1).filter(remarkable=True).order_by('-updated_on')
    })
    return context







