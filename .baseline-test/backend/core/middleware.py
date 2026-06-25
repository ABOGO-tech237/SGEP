from __future__ import annotations


class AuditMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
		if forwarded_for:
			request.audit_ip = forwarded_for.split(",")[0].strip()
		else:
			request.audit_ip = request.META.get("REMOTE_ADDR", "")
		return self.get_response(request)
