"""Throwaway verification for core.appwrite_utils against the installed SDK models."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from appwrite.models.document import Document
from appwrite.models.document_list import DocumentList
from core.appwrite_utils import to_dict, documents_of, total_of

SAMPLE_DOC = {
    "$id": "abc123",
    "$sequence": "1",
    "$collectionId": "classes",
    "$databaseId": "main",
    "$createdAt": "2026-01-01T00:00:00.000+00:00",
    "$updatedAt": "2026-01-01T00:00:00.000+00:00",
    "$permissions": [],
    "name": "Form 1A",
    "is_active": True,
}

# 1. Pydantic Document via with_data (what the SDK >= 1.8 actually returns:
#    system fields as model fields, user fields under .data)
doc_model = Document.with_data(SAMPLE_DOC)
d = to_dict(doc_model)
assert isinstance(d, dict), type(d)
assert d["$id"] == "abc123", d
assert d["name"] == "Form 1A", "user field lost!"
assert d["is_active"] is True

# 1b. Pydantic Document via plain model_validate (extras path) still works
d_mv = to_dict(Document.model_validate(SAMPLE_DOC))
assert d_mv["$id"] == "abc123" and d_mv.get("name") == "Form 1A", d_mv

# 2. Pydantic DocumentList via with_data (what list_documents returns)
dl_model = DocumentList.with_data({"total": 2, "documents": [SAMPLE_DOC, {**SAMPLE_DOC, "$id": "def456", "name": "Form 1B"}]})
docs = documents_of(dl_model)
assert isinstance(docs, list) and len(docs) == 2, docs
assert all(isinstance(x, dict) for x in docs)
assert docs[0]["$id"] == "abc123" and docs[0]["name"] == "Form 1A"
assert docs[1]["$id"] == "def456" and docs[1]["name"] == "Form 1B"
assert total_of(dl_model) == 2

# 3. Plain dict list response (older SDK behaviour)
plain = {"total": 1, "documents": [SAMPLE_DOC]}
docs2 = documents_of(plain)
assert len(docs2) == 1 and docs2[0]["name"] == "Form 1A"
assert total_of(plain) == 1

# 4. Plain dict single document
assert to_dict(SAMPLE_DOC)["name"] == "Form 1A"

# 5. Edge cases
assert to_dict(None) is None
assert documents_of({}) == []
assert total_of({}, 7) == 7

# 6. Mimic repository _normalize on a pydantic Document
def _normalize(document):
    document = to_dict(document)
    result = dict(document)
    result["id"] = document.get("$id", document.get("id"))
    return result

norm = _normalize(doc_model)
assert norm["id"] == "abc123" and norm["name"] == "Form 1A", norm

print("ALL CHECKS PASSED")
