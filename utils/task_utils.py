from django_classic.enums.util_enums import ProcessingStatus


def update_progress_info(update_info=None, status=None):
    if not update_info:
        return {"total": 0, "inserted": 0, "updated": 0, "error": 0, "corrupted": 0, "ignored": 0, }
    update_info["total"] += 1
    if status == ProcessingStatus.IGNORED or status is None:
        update_info["ignored"] += 1
    elif status == ProcessingStatus.ERROR:
        update_info["error"] += 1
    elif status == ProcessingStatus.CORRUPTED:
        update_info["corrupted"] += 1
    elif status == ProcessingStatus.INSERTED:
        update_info["inserted"] += 1
    elif status == ProcessingStatus.UPDATED:
        update_info["updated"] += 1
    return update_info
