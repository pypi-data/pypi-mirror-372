from pydantic import ValidationError


def validation_error(e: ValidationError):
    """Transform a pydantic error to user friendly error, meant to be used as `payload` of a geovisio.error"""

    details = []
    for d in e.errors():
        detail = {
            "fields": d["loc"],
            "error": d["msg"],
        }
        if d["input"]:
            detail["input"] = d["input"]
            try:
                if "user_agent" in detail["input"]:
                    del detail["input"]["user_agent"]
                if len(detail["input"]) == 0:
                    del detail["input"]
            except TypeError:
                pass
        details.append(detail)
    return {"details": details}
