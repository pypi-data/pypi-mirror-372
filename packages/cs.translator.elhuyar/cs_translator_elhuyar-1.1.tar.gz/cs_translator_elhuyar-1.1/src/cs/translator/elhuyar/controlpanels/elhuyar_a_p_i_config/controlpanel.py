from cs.translator.elhuyar import _
from cs.translator.elhuyar.interfaces import ICsTranslatorElhuyarLayer
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from zope import schema
from zope.component import adapter
from zope.interface import Interface


class IElhuyarAPIConfig(Interface):
    api_base_url = schema.TextLine(
        title=_(
            "The API base url",
        ),
        description=_(
            "",
        ),
        default="https://mt-api.elhuyar.eus",
        required=False,
        readonly=False,
    )
    translation_engine = schema.TextLine(
        title=_(
            "The API engine",
        ),
        description=_(
            "Engine for the language pair: nmt | apertium | apertiumc",
        ),
        default="nmt",
        required=False,
        readonly=False,
    )

    api_id = schema.TextLine(
        title=_(
            "The API id provided by Elhuyar",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
    )
    api_key = schema.TextLine(
        title=_(
            "The API key provided by Elhuyar",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
    )

    translatabel_css_selector = schema.TextLine(
        title=_(
            "The css selector to choose the content to translate",
        ),
        description=_(
            "",
        ),
        default="body",
        required=False,
        readonly=False,
    )

    language_pairs_to = schema.List(
        title=_(
            "Languages to give as translatable",
        ),
        description=_(
            "",
        ),
        value_type=schema.TextLine(
            title="",
        ),
        default=[],
        required=False,
        readonly=False,
    )


class ElhuyarAPIConfig(RegistryEditForm):
    schema = IElhuyarAPIConfig
    schema_prefix = "cs.translator.elhuyar.elhuyar_a_p_i_config"
    label = _("Elhuyar API Config")


ElhuyarAPIConfigView = layout.wrap_form(ElhuyarAPIConfig, ControlPanelFormWrapper)


@adapter(Interface, ICsTranslatorElhuyarLayer)
class ElhuyarAPIConfigConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IElhuyarAPIConfig
    configlet_id = "elhuyar_a_p_i_config-controlpanel"
    configlet_category_id = "Products"
    title = _("Elhuyar API Config")
    group = ""
    schema_prefix = "cs.translator.elhuyar.elhuyar_a_p_i_config"
