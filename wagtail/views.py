from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from wagtail import hooks
from wagtail.forms import PasswordViewRestrictionForm
from wagtail.models import Page, PageViewRestriction


def serve_chain(page, request, args, kwargs):
    return page.serve(request, *args, **kwargs)


def serve(request, path):
    route_result = Page.route_for_request(request, path)
    if route_result is None:
        raise Http404
    else:
        page, args, kwargs = route_result

    on_serve_chain = serve_chain
    for fn in reversed(hooks.get_hooks("on_serve_page")):
        on_serve_chain = fn(on_serve_chain)

    for fn in hooks.get_hooks("before_serve_page"):
        result = fn(page, request, args, kwargs)
        if isinstance(result, HttpResponse):
            return result
        

    return on_serve_chain(page, request, args, kwargs)


def authenticate_with_password(request, page_view_restriction_id, page_id):
    """
    Handle a submission of PasswordViewRestrictionForm to grant view access over a
    subtree that is protected by a PageViewRestriction
    """
    restriction = get_object_or_404(PageViewRestriction, id=page_view_restriction_id)
    page = get_object_or_404(Page, id=page_id).specific

    if request.method == "POST":
        form = PasswordViewRestrictionForm(request.POST, instance=restriction)
        if form.is_valid():
            return_url = form.cleaned_data["return_url"]

            if not url_has_allowed_host_and_scheme(
                return_url, request.get_host(), request.is_secure()
            ):
                return_url = settings.LOGIN_REDIRECT_URL

            restriction.mark_as_passed(request)
            return redirect(return_url)
    else:
        form = PasswordViewRestrictionForm(instance=restriction)

    action_url = reverse(
        "wagtailcore_authenticate_with_password", args=[restriction.id, page.id]
    )
    return page.serve_password_required_response(request, form, action_url)
