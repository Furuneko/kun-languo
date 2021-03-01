from django import forms


class LikertWidget(forms.RadioSelect):
    template_name = 'peq/widgets/likert.html'
    class Media:
        css = {
            'all': ('css/likert.css',)
        }

    def __init__(self, *args, **kwargs):

        self.headers = kwargs.pop('headers', {})
        self.show_values = kwargs.pop('show_values', True)
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        self.zipper = [(i[0], self.headers.get(i[0],'')) for i in self.choices]
        context = super().get_context(*args, **kwargs)
        context.update({'choices': self.choices,
                        'headers': self.headers,
                        'zipper': self.zipper,
                        'optimal_width': round(85/len(self.choices),2),
                        'show_values':self.show_values
                        })
        return context