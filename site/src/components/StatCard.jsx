import { formatNumber } from "../utils/formatters.js";

export default function StatCard({ icon: Icon, label, value, detail, tone = "cyan" }) {
  return (
    <article className={`stat-card stat-card-${tone}`}>
      <div className="stat-icon">{Icon ? <Icon size={20} /> : null}</div>
      <div>
        <p>{label}</p>
        <strong>{typeof value === "number" ? formatNumber(value) : value}</strong>
        {detail ? <span>{detail}</span> : null}
      </div>
    </article>
  );
}
