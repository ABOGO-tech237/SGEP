from __future__ import annotations

from typing import Any

"""Helpers for working with Appwrite SDK responses.

The Appwrite Python SDK (>= 1.8) returns pydantic model objects (``Document``,
``DocumentList``) instead of plain dicts. Those models no longer support
dict-style access such as ``response.get("documents")``.

In addition, ``Document`` stores the user-defined fields (``email``, ``name``,
...) separately from the system fields (``$id``, ``$createdAt``, ...): the
system fields are regular model fields while the user data lives under the
``.data`` attribute. Neither ``model_dump()`` nor ``DocumentList.model_dump()``
flattens that user data back in, so we flatten it explicitly here.

These helpers normalize either form (a plain dict from older SDKs or a pydantic
model from newer ones) into a flat plain dict so the repository code keeps
working regardless of SDK version.
"""


def install_appwrite_get_body_shim() -> None:
	"""Stop the Appwrite Python SDK from sending a body on GET requests.

	Appwrite Cloud rejects GET requests that carry a JSON body (HTTP 400:
	``request cannot have request body``). SDK 7.x serializes empty params to
	``"{}"`` and sends it as a body on GET requests. Stripping the content-type
	header makes the SDK skip ``json.dumps`` and send no body.
	"""
	from appwrite.client import Client

	if getattr(Client, "_sgep_get_body_shim", False):
		return

	_original_call = Client.call

	def _patched_call(self, method, path="", headers=None, params=None, response_type="json"):
		if str(method).lower() == "get":
			headers = dict(headers or {})
			headers["content-type"] = ""
		return _original_call(self, method, path, headers, params, response_type)

	Client.call = _patched_call
	Client._sgep_get_body_shim = True


def _user_data(obj: Any) -> dict | None:
	"""Return the user-defined fields stored on an Appwrite Document, if any."""
	data = getattr(obj, "_data", None)
	if data is None:
		try:
			data = obj.data
		except Exception:  # noqa: BLE001 - property may be absent
			data = None
	if isinstance(data, dict):
		return data
	model_dump = getattr(data, "model_dump", None)
	if callable(model_dump):
		return model_dump(mode="json")
	return None


def to_dict(obj: Any) -> Any:
	"""Normalize an Appwrite response/document into a flat plain dict.

	Returns ``obj`` unchanged when it is already a dict (or when it cannot be
	converted), and ``None`` for ``None`` inputs.
	"""
	if obj is None:
		return None
	if isinstance(obj, dict):
		return obj

	base: dict = {}
	model_dump = getattr(obj, "model_dump", None)
	if callable(model_dump):
		base = model_dump(by_alias=True, mode="json")

	# Appwrite Document keeps user-defined fields under `.data`; merge them back
	# in so callers see a flat document (e.g. {"$id": ..., "email": ...}).
	data = _user_data(obj)
	if data:
		return {**base, **data}

	if base:
		return base

	to_dict_method = getattr(obj, "to_dict", None)
	if callable(to_dict_method):
		return to_dict_method()
	return obj


def documents_of(response: Any) -> list:
	"""Return the documents list (as flat plain dicts) from a list response."""
	if response is None:
		return []
	if isinstance(response, dict):
		documents = response.get("documents", []) or []
	else:
		documents = getattr(response, "documents", None)
		if documents is None:
			data = to_dict(response)
			documents = data.get("documents", []) if isinstance(data, dict) else []
		documents = documents or []
	return [to_dict(document) for document in documents]


def total_of(response: Any, default: int = 0) -> int:
	"""Return the total count from a list response."""
	if response is None:
		value: Any = default
	elif isinstance(response, dict):
		value = response.get("total", default)
	else:
		value = getattr(response, "total", default)
	return int(value or 0)


def install_get_body_shim() -> None:
	"""Stop the Appwrite SDK from sending a body on GET requests (Cloud rejects it)."""
	from appwrite.client import Client

	if getattr(Client, "_sgep_get_body_shim", False):
		return

	_original_call = Client.call

	def _patched_call(self, method, path="", headers=None, params=None, response_type="json"):
		if str(method).lower() == "get":
			headers = dict(headers or {})
			headers["content-type"] = ""
		return _original_call(self, method, path, headers, params, response_type)

	Client.call = _patched_call
	Client._sgep_get_body_shim = True
