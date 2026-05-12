#!/usr/bin/env python3
"""Export lightweight JSON files for the static React dashboard."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODES_CSV = ROOT / "data" / "clean" / "neo4j_graph_nodes.csv"
EDGES_CSV = ROOT / "data" / "clean" / "neo4j_email_edges.csv"
OUT_DIR = ROOT / "site" / "public" / "data"

MAX_GRAPH_NODES = 180
MAX_GRAPH_LINKS = 450
MIN_LINK_WEIGHT = 2


def to_int(value: str | None) -> int:
    if value is None or value == "":
        return 0
    return int(float(value))


def read_nodes() -> list[dict]:
    with NODES_CSV.open(newline="", encoding="utf-8-sig") as handle:
        rows = []
        for row in csv.DictReader(handle):
            person_id = (row.get("person_id") or "").strip()
            if not person_id:
                continue
            rows.append(
                {
                    "id": person_id,
                    "label": person_id,
                    "sent_count": to_int(row.get("sent_count")),
                    "received_count": to_int(row.get("received_count")),
                    "total_count": to_int(row.get("total_count")),
                }
            )
    return sorted(rows, key=lambda item: item["total_count"], reverse=True)


def read_edges() -> list[dict]:
    with EDGES_CSV.open(newline="", encoding="utf-8-sig") as handle:
        rows = []
        for row in csv.DictReader(handle):
            source = (row.get("source") or "").strip()
            target = (row.get("target") or "").strip()
            if not source or not target:
                continue
            rows.append(
                {
                    "source": source,
                    "target": target,
                    "weight": to_int(row.get("weight")),
                    "first_date": row.get("first_date") or "",
                    "last_date": row.get("last_date") or "",
                    "recipient_types": row.get("recipient_types") or "",
                }
            )
    return sorted(rows, key=lambda item: item["weight"], reverse=True)


def build_graph(nodes: list[dict], edges: list[dict]) -> dict:
    active_nodes = nodes[:MAX_GRAPH_NODES]
    active_ids = {node["id"] for node in active_nodes}

    links = [
        edge
        for edge in edges
        if edge["weight"] >= MIN_LINK_WEIGHT
        and edge["source"] in active_ids
        and edge["target"] in active_ids
    ][:MAX_GRAPH_LINKS]

    used_ids = {link["source"] for link in links} | {link["target"] for link in links}
    visible_nodes = [node for node in active_nodes if node["id"] in used_ids]

    return {"nodes": visible_nodes, "links": links}


def build_stats(nodes: list[dict], edges: list[dict], graph: dict) -> dict:
    strongest = edges[0] if edges else None
    central = nodes[0] if nodes else None
    return {
        "node_count": len(nodes),
        "relation_count": len(edges),
        "total_email_relations": sum(edge["weight"] for edge in edges),
        "strongest_relation": strongest,
        "most_connected_person": central,
        "graph_node_count": len(graph["nodes"]),
        "graph_link_count": len(graph["links"]),
        "graph_limits": {
            "max_nodes": MAX_GRAPH_NODES,
            "max_links": MAX_GRAPH_LINKS,
            "min_link_weight": MIN_LINK_WEIGHT,
        },
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not NODES_CSV.exists():
        raise FileNotFoundError(f"Missing nodes CSV: {NODES_CSV}")
    if not EDGES_CSV.exists():
        raise FileNotFoundError(f"Missing edges CSV: {EDGES_CSV}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    nodes = read_nodes()
    edges = read_edges()
    graph = build_graph(nodes, edges)
    stats = build_stats(nodes, edges, graph)

    write_json(OUT_DIR / "nodes.json", nodes)
    write_json(OUT_DIR / "edges.json", edges)
    write_json(OUT_DIR / "graph.json", graph)
    write_json(OUT_DIR / "stats.json", stats)

    print(f"Exported {len(nodes)} nodes and {len(edges)} edges to {OUT_DIR}")
    print(f"Graph preview: {len(graph['nodes'])} nodes, {len(graph['links'])} links")


if __name__ == "__main__":
    main()
