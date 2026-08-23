import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.checklist_modal import ChecklistModal


def apply_changes_to_lists(app, target_media_info, changes):
    if not changes:
        return False

    lists_updated = False

    for list_id, value in changes.items():
        if value == 1:
            database.add_list_item(
                app.db,
                target_media_info,
                list_id,
            )
            lists_updated = True
        elif value == -1:
            database.delete_list_item(
                app.db,
                target_media_info,
                list_id,
            )
            lists_updated = True

    return lists_updated
