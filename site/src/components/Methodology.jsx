import { ArrowRight, Database, Filter, GitBranch, Network, Sparkles } from "lucide-react";

const steps = [
  {
    icon: Database,
    title: "Collecte API JMail",
    text: "Récupération des index et détails d'emails depuis des sources ouvertes.",
  },
  {
    icon: Sparkles,
    title: "Nettoyage Python",
    text: "Transformation des exports bruts en tables propres et réutilisables.",
  },
  {
    icon: Filter,
    title: "Normalisation des noms",
    text: "Regroupement des variantes de noms, emails et libellés de personnes.",
  },
  {
    icon: Filter,
    title: "Suppression du bruit",
    text: "Exclusion des valeurs Unknown, Redacted et des entrées non exploitables.",
  },
  {
    icon: ArrowRight,
    title: "Construction source -> target",
    text: "Agrégation des emails en relations pondérées entre expéditeurs et destinataires.",
  },
  {
    icon: Network,
    title: "Analyse par graphes",
    text: "Lecture des centralités, intensités relationnelles et limites de couverture.",
  },
];

export default function Methodology() {
  return (
    <section className="methodology">
      <div className="section-heading">
        <span className="eyebrow">Pipeline reproductible</span>
        <h2>Méthodologie</h2>
      </div>
      <div className="method-grid">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <article className="method-card" key={step.title}>
              <Icon size={20} />
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </article>
          );
        })}
      </div>
      <div className="interpretation">
        <GitBranch size={22} />
        <div>
          <h2>Interprétation</h2>
          <p>
            Acteurs centraux : compléter avec les personnes ayant les volumes
            entrants et sortants les plus élevés, en distinguant activité brute
            et rôle structurel dans le réseau.
          </p>
          <p>
            Relations fortes : analyser les arêtes les plus pondérées comme des
            canaux de communication récurrents, puis les confronter à la période
            observée.
          </p>
          <p>
            Limites des données : signaler les emails incomplets, les personnes
            anonymisées, les alias imparfaits et le fait qu'une fréquence élevée
            ne prouve pas à elle seule une proximité sociale.
          </p>
          <p>
            Intérêt de Neo4j et des graphes : représenter explicitement les
            personnes, les directions d'échange et les poids permet de passer
            d'une liste d'emails à une lecture relationnelle du système.
          </p>
        </div>
      </div>
    </section>
  );
}
