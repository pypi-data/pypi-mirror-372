import os

from . import CONFIG


def clean_api_docs():
    doc_api_path = os.path.join(CONFIG.docs, "api")
    if not os.path.isdir(doc_api_path):
        return

    walk = list(os.walk(doc_api_path))
    for root, dirs, files in walk:
        for f in files:
            af = os.path.abspath(os.path.join(root, f))

            if f == "index.rst":  # don't remove index file(s)
                continue

            if f.endswith(".rst"):
                os.remove(af)

    for root, _, _ in walk:
        if root == doc_api_path:
            continue

        try:
            os.rmdir(root)
        except OSError:
            pass
