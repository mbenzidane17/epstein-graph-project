import { formatNumber } from "../utils/formatters.js";

export default function TopActorsTable({ nodes }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <span className="eyebrow">Centralité opérationnelle</span>
        <h2>Top acteurs</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Personne</th>
              <th>Envoyés</th>
              <th>Reçus</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {nodes.slice(0, 12).map((node, index) => (
              <tr key={node.id}>
                <td>{index + 1}</td>
                <td className="entity-cell">{node.label}</td>
                <td>{formatNumber(node.sent_count)}</td>
                <td>{formatNumber(node.received_count)}</td>
                <td>
                  <span className="badge">{formatNumber(node.total_count)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
