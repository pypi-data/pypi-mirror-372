
from django import template
from ..models import ModalImageOnly, ModalSingleBG, ModalLinkVideo, ModalRotateBG

register = template.Library()

TEMPLATE_MAP = {
    ModalRotateBG: "modal_hj3415/rotate_bg.html",
    ModalLinkVideo: "modal_hj3415/link_video.html",
    ModalSingleBG: "modal_hj3415/single_bg.html",
    ModalImageOnly: "modal_hj3415/image_only.html",
}

MODEL_ORDER = {
    "image_only": ModalImageOnly,
    "single_bg": ModalSingleBG,
    "link_video": ModalLinkVideo,
    "rotate_bg": ModalRotateBG,
}

@register.inclusion_tag("modal_hj3415/_load.html")
def show_modal(auto_open=True, priority=("image_only", "single_bg", "link_video", "rotate_bg")):
    popup, model = None, None
    for key in priority:
        M = MODEL_ORDER[key]
        popup = M.objects.filter(activate=True).order_by("-id").first()  # 가장 최신 것
        if popup:
            model = M
            break

    if not popup:
        return {"popup": None}  # 템플릿에서 {% if popup %}로 처리

    modal_id = f"popupModal-{model.__name__}-{popup.pk}"
    template_name = TEMPLATE_MAP[model]
    return {
        "dont_show_again": "다시보지않기",
        "popup": popup,
        "template_name": template_name,
        "modal_id": modal_id,
        "auto_open": auto_open,
    }

@register.inclusion_tag("modal_hj3415/_load_many.html")
def show_modals(
    auto_open=True,
    priority=("image_only", "single_bg", "link_video", "rotate_bg"),
    only_latest=False,
):
    """
    활성화된 모든 모달을 우선순위대로 수집해 순차적으로(큐) 표시.
    단일 태그와 동일한 규약(template_name/modal_id)으로 내려줍니다.
    """
    items = []
    for key in priority:
        M = MODEL_ORDER[key]
        qs = M.objects.filter(activate=True).order_by("-id")
        if only_latest:
            qs = qs[:1]
        for popup in qs:
            items.append({
                "popup": popup,
                "template_name": TEMPLATE_MAP[M],
                "modal_id": f"popupModal-{M.__name__}-{popup.pk}",
                "title": getattr(popup, "modal_title", M.__name__),
            })

    return {
        "dont_show_again": "다시보지않기",
        "items": items,
        "auto_open": auto_open,
    }