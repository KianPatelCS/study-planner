from sr_study import Card, apply_sm2

def test_fail_resets_progress():
    c = Card(id=1, front="f", back="b", tags=[])
    apply_sm2(c, 2)
    assert c.reps == 0
    assert c.interval == 1

def test_easy_increases_interval_and_ef():
    c = Card(id=1, front="f", back="b", tags=[], ef=2.5, interval=3, reps=3)
    old_ef = c.ef
    apply_sm2(c, 5)
    assert c.interval >= 3
    assert c.ef >= old_ef
