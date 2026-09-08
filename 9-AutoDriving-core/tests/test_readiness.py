from dataclasses import replace
import itertools
import math
import pytest
from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route


def test_unknown_category_not_silently_dropped():
    result = ExactRouteSolver(generate_synthetic_graph()).solve(["pharmacy", "hospital"])
    assert result.status == "INVALID_INTENT" and not result.is_valid


def test_empty_route_checks_deadline():
    result = ExactRouteSolver(generate_synthetic_graph()).solve([], time_limit=1)
    assert not result.is_valid


def test_mall_alias_dependency_is_enforced():
    result = ExactRouteSolver(generate_synthetic_graph()).solve(
        ["shopping_mall", "bank"], dependencies=[("shopping mall", "bank")])
    assert result.categories == ("shopping_mall", "bank")


@pytest.mark.parametrize("value", [-1, 1.1, float("nan"), True])
def test_invalid_weights_rejected(value):
    assert not ExactRouteSolver(generate_synthetic_graph()).solve(["bank"], quality_weight=value).is_valid


@pytest.mark.parametrize("value", ["18:99", "25:00", "unknown", -1, True])
def test_invalid_time_rejected(value):
    assert not ExactRouteSolver(generate_synthetic_graph()).solve(["bank"], time_limit=value).is_valid


def test_gold_checker_catches_dropped_deadline():
    graph = generate_synthetic_graph()
    result = ExactRouteSolver(graph).solve(["bank"])
    gold = Intent.parse({"pois": ["bank"], "time_limit": 541, "dependencies": [], "quality_weight": .5})
    assert result.is_valid and not check_route(graph, result, gold)["task_success"]


def test_closed_store_and_waiting():
    graph = generate_synthetic_graph()
    banks = [p for p in graph.pois if p.category == "bank"]
    graph.pois = [replace(p, open_time=700, close_time=720, stay_duration=30) for p in banks]
    assert not ExactRouteSolver(graph).solve(["bank"]).is_valid
    graph.pois = [replace(p, close_time=800) for p in graph.pois]
    result = ExactRouteSolver(graph).solve(["bank"])
    assert result.is_valid and result.final_arrival_time >= 730


def test_serialization_does_not_change_objective(tmp_path):
    graph = generate_synthetic_graph()
    graph.save(tmp_path / "graph.json")
    restored = type(graph).load(tmp_path / "graph.json")
    assert graph.max_edge_distance == restored.max_edge_distance
    assert ExactRouteSolver(graph).solve(["bank", "library"]) == ExactRouteSolver(restored).solve(["bank", "library"])


def test_two_category_exhaustive_independent_objective():
    graph = generate_synthetic_graph(seed=63)
    w = .37
    candidates = []
    for bank, library in itertools.product([p for p in graph.pois if p.category == "bank"],
                                            [p for p in graph.pois if p.category == "library"]):
        for seq in [(bank, library), (library, bank)]:
            coords = [graph.origin] + [(p.x, p.y) for p in seq] + [graph.destination]
            dist = sum(math.dist(a, b) for a, b in zip(coords, coords[1:]))
            value = w * sum(p.quality for p in seq) / 2 - (1-w) * dist / (6*graph.max_edge_distance)
            candidates.append((value, tuple(p.id for p in seq)))
    expected = sorted(candidates, key=lambda x: (-x[0], x[1]))[0]
    result = ExactRouteSolver(graph).solve(["bank", "library"], quality_weight=w)
    assert result.poi_ids == expected[1]
    assert abs(result.utility - expected[0]) <= .00005


def test_preprocessing_uses_canonical_dependency_and_strict_time():
    from src.preprocess_hipp import compute_transitive_closure, normalize_time_limit
    assert compute_transitive_closure([["shopping mall", "bank"]]) == (("shopping_mall", "bank"),)
    assert normalize_time_limit("24:00") == 1440
    with pytest.raises(ValueError):
        normalize_time_limit("25:00")


def test_chat_transport_forwards_output_budget(monkeypatch):
    from src import llm_client
    captured = {}
    def fake_post(url, payload, key, timeout):
        captured.update(payload)
        return {"choices": [{"message": {"content": "{}"}}]}
    monkeypatch.setattr(llm_client, "post_json", fake_post)
    config = llm_client.LLMConfig(max_output_tokens=1600)
    client = llm_client.OpenAICompatibleChatClient(config, "test-placeholder")
    client.complete({"system_prompt": "JSON", "user_prompt": "test"})
    assert captured["max_completion_tokens"] == 1600
