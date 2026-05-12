import { formatDate, formatNumber } from "../utils/formatters.js";

export default function TopRelationsTable({ edges }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <span className="eyebrow">Arêtes pondérées</span>
        <h2>Top relations</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Source</th>
              <th>Cible</th>
              <th>Poids</th>
              <th>Période</th>
            </tr>
          </thead>
          <tbody>
            {edges.slice(0, 12).map((edge, index) => (
              <tr key={`${edge.source}-${edge.target}-${index}`}>
                <td>{index + 1}</td>
                <td className="entity-cell">{edge.source}</td>
                <td className="entity-cell">{edge.target}</td>
                <td>
                  <span className="badge badge-warm">{formatNumber(edge.weight)}</span>
                </td>
                <td>{formatDate(edge.first_date)} - {formatDate(edge.last_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
