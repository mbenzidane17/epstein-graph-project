# Epstein Graph Project

Projet universitaire d’analyse de réseau à partir d’emails issus de l’API JMail.

L’objectif du projet est de construire un graphe de communications afin d’identifier les principaux acteurs, les relations les plus fréquentes et la structure générale des échanges.

Le projet contient deux parties :

- une partie **Python** pour l’extraction, le nettoyage et la construction du graphe ;
- une partie **React / Vite** pour visualiser les résultats sous forme de dashboard interactif.

Dashboard en ligne : https://epsteindashboard.netlify.app/

---

## Structure du projet

```text
.
├── src/
│   ├── 01_inspect_api_jmail.py
│   ├── 02_export_jmail_index.py
│   ├── 03_clean_senders.py
│   ├── 04_build_person_nodes.py
│   ├── 05_inspect_email_detail.py
│   ├── 05_inspect_thread_api.py
│   ├── 06_fetch_thread_details.py
│   ├── 07_build_email_edges.py
│   └── 08_export_site_data.py
│
├── data/
│   └── clean/
│       ├── jmail_email_index.csv
│       ├── jmail_email_index_clean.csv
│       ├── message_recipients.csv
│       ├── neo4j_email_edges.csv
│       └── neo4j_graph_nodes.csv
│
├── site/
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   └── data/
│   │       ├── edges.json
│   │       ├── graph.json
│   │       ├── nodes.json
│   │       └── stats.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       ├── components/
│       └── utils/
│
├── requirements.txt
├── .gitignore
└── README.md

