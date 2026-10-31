from productivity.store import Store


def test_tasks_get_increasing_ids_and_persist(tmp_path):
    store = Store(tmp_path / "d.json")
    assert store.add_task("A", None, "low").id == 1
    assert store.add_task("B", "2026-11-05", "high").id == 2
    again = Store(tmp_path / "d.json")              # a fresh object reads the file
    assert [t.title for t in again.tasks("all")] == ["A", "B"]


def test_status_filters(tmp_path):
    store = Store(tmp_path / "d.json")
    store.add_task("A", None, "low")
    store.add_task("B", None, "low")
    store.complete_task(1)
    assert [t.id for t in store.tasks("open")] == [2]
    assert [t.id for t in store.tasks("done")] == [1]
    assert len(store.tasks("all")) == 2


def test_missing_task_raises_lookup_error(tmp_path):
    store = Store(tmp_path / "d.json")
    for action in (store.get_task, store.complete_task, store.delete_task):
        try:
            action(7)
        except LookupError as exc:
            assert "no task 7" in str(exc)
        else:
            raise AssertionError("expected LookupError")


def test_save_leaves_no_temp_file(tmp_path):
    store = Store(tmp_path / "d.json")
    store.add_note("wifi", "on the router")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["d.json"]


def test_search_notes_matches_title_or_text_ignoring_case(tmp_path):
    store = Store(tmp_path / "d.json")
    store.add_note("Wifi", "password on the router")
    store.add_note("Ideas", "learn about routers")
    assert [n.id for n in store.search_notes("ROUTER")] == [1, 2]
    assert [n.id for n in store.search_notes("wifi")] == [1]
