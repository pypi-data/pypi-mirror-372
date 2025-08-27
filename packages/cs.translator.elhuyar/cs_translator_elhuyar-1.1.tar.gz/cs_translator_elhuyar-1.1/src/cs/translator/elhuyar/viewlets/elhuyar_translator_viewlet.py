from plone import api
from plone.app.layout.viewlets import ViewletBase


class ElhuyarTranslatorViewlet(ViewletBase):
    def index(self):
        return super().render()

    def language_options(self):
        language_pairs_to = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.language_pairs_to"
        )
        return language_pairs_to

    def selector(self):
        translatabel_css_selector = api.portal.get_registry_record(
            "cs.translator.elhuyar.elhuyar_a_p_i_config.translatabel_css_selector"
        )
        return translatabel_css_selector
