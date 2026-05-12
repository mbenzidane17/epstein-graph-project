import { useEffect, useMemo, useState } from "react";
import { Mail, Network, RadioTower, Star, Users } from "lucide-react";
import GraphView from "./components/GraphView.jsx";
import Methodology from "./components/Methodology.jsx";
import StatCard from "./components/StatCard.jsx";
import TopActorsTable from "./components/TopActorsTable.jsx";
import TopRelationsTable from "./components/TopRelationsTable.jsx";
import { formatNumber, shortName } from "./utils/formatters.js";

const dataFiles = {
  nodes: `${import.meta.env.BASE_URL}data/nodes.json`,
  edges: `${import.meta.env.BASE_URL}data/edges.json`,
  stats: `${import.meta.env.BASE_URL}data/stats.json`,
  graph: `${import.meta.env.BASE_URL}data/graph.json`,
};

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all(
      Object.entries(dataFiles).map(([key, url]) =>
        fetch(url).then((response) => {
          if (!response.ok) throw new Error(`Impossible de charger ${url}`);
          return response.json().then((json) => [key, json]);
        }),
      ),
    )
      .then((entries) => setData(Object.fromEntries(entries)))
      .catch((err) => setError(err.message));
  }, []);

  const actorChart = useMemo(() => {
    if (!data?.nodes) return [];
    return data.nodes.slice(0, 8).map((node) => ({
      name: shortName(node.label, 16),
      total: node.total_count,
    }));
  }, [data]);

  if (error) {
    return (
      <main className="app app-centered">
        <div className="load-card">
          <h1>Epstein Graph</h1>
          <p>{error}</p>
          <span>Lancez d'abord python3 src/08_export_site_data.py depuis la racine.</span>
        </div>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="app app-centered">
        <div className="load-card">
          <h1>Epstein Graph</h1>
          <p>Chargement des données du graphe...</p>
        </div>
      </main>
    );
  }

  const { nodes, edges, stats, graph } = data;
  const strongest = stats.strongest_relation;
  const central = stats.most_connected_person;

  return (
    <main className="app">
      <section className="hero">
        <div className="hero-copy">
          <span className="kicker">MIAGE - théorie des graphes</span>
          <h1>Epstein Graph</h1>
          <p>
            Analyse d'un réseau email open data par théorie des graphes :
            collecte JMail, nettoyage Python, agrégation des relations et
            visualisation interactive des acteurs centraux.
          </p>
        </div>
        <div className="hero-panel">
          <span>Graphe exporté</span>
          <strong>{formatNumber(stats.graph_node_count)} nœuds</strong>
          <p>{formatNumber(stats.graph_link_count)} relations fortes affichées</p>
        </div>
      </section>

      <section className="stats-grid">
        <StatCard icon={Users} label="Nœuds" value={stats.node_count} detail="personnes identifiées" />
        <StatCard icon={Network} label="Relations" value={stats.relation_count} detail="arêtes source -> target" tone="green" />
        <StatCard icon={Mail} label="Emails analysés" value={stats.total_email_relations} detail="somme des poids" tone="amber" />
        <StatCard
          icon={RadioTower}
          label="Relation la plus forte"
          value={strongest ? formatNumber(strongest.weight) : "n/a"}
          detail={strongest ? `${shortName(strongest.source, 18)} -> ${shortName(strongest.target, 18)}` : ""}
          tone="rose"
        />
        <StatCard
          icon={Star}
          label="Personne la plus connectée"
          value={central ? shortName(central.label, 24) : "n/a"}
          detail={central ? `${formatNumber(central.total_count)} emails` : ""}
          tone="violet"
        />
      </section>

      <section className="chart-panel">
        <div className="section-heading">
          <span className="eyebrow">Volume total</span>
          <h2>Acteurs les plus actifs</h2>
        </div>
        <div className="bar-list">
          {actorChart.map((item) => {
            const max = actorChart[0]?.total || 1;
            const width = `${Math.max(8, (item.total / max) * 100)}%`;
            return (
              <div className="bar-row" key={item.name}>
                <span>{item.name}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width }} />
                </div>
                <strong>{formatNumber(item.total)}</strong>
              </div>
            );
          })}
        </div>
      </section>

      <GraphView graph={graph} />

      <section className="tables-grid">
        <TopActorsTable nodes={nodes} />
        <TopRelationsTable edges={edges} />
      </section>

      <Methodology />
    </main>
  );
}
