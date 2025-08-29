from shared_lib import utils
from _data import medicio, shared_lib


c = medicio.context
c.update(shared_lib.analytics)


def medicio_home(request):
    return utils.home(request,'medicio/index.html', c)

# 이후의 함수 및 클래스에 컨택스트를 전달하는 이유는 color 변수 때문으로 다른 템플릿에서는 전달할 필요 없다.

def medicio_terms(request):
    return utils.terms(request, 'medicio/pages/terms.html', c)

def medicio_privacy(request):
    return utils.privacy(request, 'medicio/pages/privacy.html', c)

def medicio_portfolio_details(request, pk):
    return utils.portfolio_details(request, 'medicio/pages/portfolio_details.html', pk, c)



class MedicioBlogDetailView(utils.BlogDetailView):
    template_name = "medicio/pages/blog_details.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(c)
        return context

