from src.conflits import detecter_conflits


def types(c):
    return sorted({x["type"] for x in c})


def test_programme_realiste_sans_conflit():
    s = [{"id": "A", "debut": "2026-11-16T17:00", "fin": "2026-11-16T18:00"},
         {"id": "B", "debut": "2026-11-16T18:30", "fin": "2026-11-16T19:30"}]
    assert detecter_conflits(s) == []


def test_chevauchement():
    s = [{"id": "A", "titre": "Maths", "debut": "2026-11-16T17:00", "fin": "2026-11-16T18:30"},
         {"id": "B", "titre": "Anglais", "debut": "2026-11-16T18:00", "fin": "2026-11-16T19:00"}]
    c = detecter_conflits(s)
    assert types(c) == ["chevauchement"]
    assert "Maths" in c[0]["message"] and "Anglais" in c[0]["message"]


def test_surcharge_journaliere():
    s = [{"id": f"S{i}", "debut": f"2026-11-16T{8 + 2 * i:02d}:00", "fin": f"2026-11-16T{9 + 2 * i:02d}:50"}
         for i in range(4)]
    assert "surcharge" in types(detecter_conflits(s, max_minutes_jour=360))


def test_repos_insuffisant():
    s = [{"id": "A", "debut": "2026-11-16T17:00", "fin": "2026-11-16T18:00"},
         {"id": "B", "debut": "2026-11-16T18:05", "fin": "2026-11-16T19:00"}]
    assert types(detecter_conflits(s, repos_minutes=10)) == ["repos"]


def test_jours_differents_pas_de_repos_requis():
    s = [{"id": "A", "debut": "2026-11-16T22:00", "fin": "2026-11-16T23:00"},
         {"id": "B", "debut": "2026-11-17T08:00", "fin": "2026-11-17T09:00"}]
    assert detecter_conflits(s) == []


def test_sessions_non_ordonnees():
    s = [{"id": "B", "debut": "2026-11-16T18:00", "fin": "2026-11-16T19:00"},
         {"id": "A", "debut": "2026-11-16T17:30", "fin": "2026-11-16T18:30"}]
    assert types(detecter_conflits(s)) == ["chevauchement"]
