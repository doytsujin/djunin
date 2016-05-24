# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile
import logging

logger = logging.getLogger(__name__)

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
	EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


# see: http://onecreativeblog.com/post/59051248/django-login-required-middleware
class LoginRequiredMiddleware:
	"""
	Middleware that requires a user to be authenticated to view any page other
	than LOGIN_URL. Exemptions to this requirement can optionally be specified
	in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
	you can copy from your urls.py).

	Requires authentication middleware and template context processors to be
	loaded. You'll get an error if they aren't.
	"""
	def process_request(self, request):
		assert hasattr(request, 'user'), "The Login Required middleware\
requires authentication middleware to be installed. Edit your\
MIDDLEWARE_CLASSES setting to insert\
'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
'django.core.context_processors.auth'."
		if not request.user.is_authenticated():
			path = request.path_info.lstrip('/')
			if not any(m.match(path) for m in EXEMPT_URLS):
				return HttpResponseRedirect(settings.LOGIN_URL + '?next=%s' % request.path_info)


class ExceptionLoggingMiddleware(object):
	def process_exception(self, request, exception):
		logger.exception("Uncaught error %s for %s" % (exception, request.path), exception)