import { useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { Activity, MousePointer2 } from "lucide-react";
import { formatDate, formatNumber } from "../utils/formatters.js";

function nodeRadius(node) {
  return Math.max(4, Math.min(18, Math.sqrt(node.total_count || 1) * 0.45));
}

export default function GraphView({ graph }) {
  const containerRef = useRef(null);
  const [selected, setSelected] = useState(null);

  const graphData = useMemo(
    () => ({
      nodes: graph.nodes?.map((node) => ({ ...node })) || [],
      links: graph.links?.map((link) => ({ ...link })) || [],
    }),
    [graph],
  );

  const selectedType = selected?.source && selected?.target ? "relation" : "node";

  return (
    <section className="graph-section">
      <div className="graph-header">
        <div>
          <span className="eyebrow">Visualisation interactive</span>
          <h2>Graphe email</h2>
        </div>
        <div className="graph-meta">
          <span>{formatNumber(graphData.nodes.length)} nœuds</span>
          <span>{formatNumber(graphData.links.length)} liens</span>
        </div>
      </div>
      <div className="graph-shell" ref={containerRef}>
        <ForceGraph2D
          graphData={graphData}
          height={620}
          backgroundColor="rgba(7, 14, 24, 0)"
          nodeRelSize={1}
          cooldownTicks={80}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          linkColor={(link) =>
            selected === link ? "rgba(248, 196, 113, 0.95)" : "rgba(114, 190, 205, 0.28)"
          }
          linkWidth={(link) => Math.max(1, Math.min(8, Math.sqrt(link.weight || 1) * 0.55))}
          linkDirectionalParticles={(link) => (selected === link ? 4 : 0)}
          linkDirectionalParticleWidth={2}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const radius = nodeRadius(node);
            const isSelected = selected === node;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = isSelected ? "#f8c471" : "#69d2e7";
            ctx.shadowColor = isSelected ? "rgba(248, 196, 113, 0.8)" : "rgba(105, 210, 231, 0.35)";
            ctx.shadowBlur = isSelected ? 18 : 8;
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = "rgba(255, 255, 255, 0.75)";
            ctx.lineWidth = 0.8;
            ctx.stroke();

            if (globalScale > 1.15 || isSelected) {
              const label = node.label;
              const fontSize = Math.max(8, 12 / globalScale);
              ctx.font = `${fontSize}px Inter, system-ui, sans-serif`;
              ctx.fillStyle = "rgba(235, 245, 247, 0.9)";
              ctx.fillText(label, node.x + radius + 3, node.y + fontSize / 3);
            }
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeRadius(node) + 4, 0, 2 * Math.PI, false);
            ctx.fill();
          }}
          onNodeHover={(node) => node && setSelected(node)}
          onLinkHover={(link) => link && setSelected(link)}
          onNodeClick={setSelected}
          onLinkClick={setSelected}
        />
        <aside className="inspector">
          <div className="inspector-title">
            {selected ? <Activity size={18} /> : <MousePointer2 size={18} />}
            <strong>{selected ? (selectedType === "relation" ? "Relation" : "Personne") : "Inspection"}</strong>
          </div>
          {selected ? (
            selectedType === "relation" ? (
              <dl>
                <dt>Source</dt>
                <dd>{selected.source.id || selected.source}</dd>
                <dt>Cible</dt>
                <dd>{selected.target.id || selected.target}</dd>
                <dt>Poids</dt>
                <dd>{formatNumber(selected.weight)}</dd>
                <dt>Période</dt>
                <dd>{formatDate(selected.first_date)} - {formatDate(selected.last_date)}</dd>
              </dl>
            ) : (
              <dl>
                <dt>Nom</dt>
                <dd>{selected.label}</dd>
                <dt>Emails envoyés</dt>
                <dd>{formatNumber(selected.sent_count)}</dd>
                <dt>Emails reçus</dt>
                <dd>{formatNumber(selected.received_count)}</dd>
                <dt>Total</dt>
                <dd>{formatNumber(selected.total_count)}</dd>
              </dl>
            )
          ) : (
            <p>Survolez ou cliquez un nœud ou une relation pour afficher ses détails.</p>
          )}
        </aside>
      </div>
    </section>
  );
}
