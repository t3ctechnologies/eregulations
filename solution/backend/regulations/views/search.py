from django.views.generic.base import TemplateView


class SearchView(TemplateView):
    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()

        c = {
            'host': host
         }

        return {**context, **c, **self.request.GET.dict()}
