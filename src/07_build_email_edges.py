import json
import os
import re
import pandas as pd

INPUT_FILE = "data/raw/thread_details.jsonl"

OUTPUT_RECIPIENTS = "data/clean/message_recipients.csv"
OUTPUT_EDGES = "data/clean/neo4j_email_edges.csv"
OUTPUT_NODES = "data/clean/neo4j_graph_nodes.csv"

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


EMAIL_MAP = {
    "jeeproject@yahoo.com": "Jeffrey Epstein",
    "jeevacation@gmail.com": "Jeffrey Epstein",
    "littlestjeff@yahoo.com": "Jeffrey Epstein",

    "gmax1@ellmax.com": "Ghislaine Maxwell",
    "gmax1@mindspring.com": "Ghislaine Maxwell",

    "lesley@nysgllc.com": "Lesley Groff",
    "rkahn@nysgmail.com": "Richard Kahn",
    "ehbarak1@gmail.com": "Ehud Barak",
}


NAME_MAP = {
    "j. epstein": "Jeffrey Epstein",
    "jeffrey epstein": "Jeffrey Epstein",
    "jeffrey e": "Jeffrey Epstein",
    "jeffrey e.": "Jeffrey Epstein",

    "gmax": "Ghislaine Maxwell",
    "g. max": "Ghislaine Maxwell",
    "ghislaine maxwell": "Ghislaine Maxwell",

    "lesley groff": "Lesley Groff",

    "rich kahn": "Richard Kahn",
    "richard kahn": "Richard Kahn",

    "ehud barak": "Ehud Barak",
}


BAD_PATTERNS = [
    "unknown",
    "redacted",
    "blacked",
    "mailto",
    "█",
    "content is blacked out",
    "information obscured",
    "information redacted",
]


def clean_text(value):
    if value is None or pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace('"', "")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def extract_email(value):
    value = clean_text(value).lower()
    match = EMAIL_RE.search(value)

    if match:
        return match.group(0).lower()

    return ""


def extract_name(value):
    value = clean_text(value)

    if "<" in value:
        value = value.split("<")[0]

    value = re.sub(r"\[mailto:.*?\]", "", value, flags=re.IGNORECASE)
    value = value.replace("[", "").replace("]", "")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def is_bad_identity(value):
    value = clean_text(value).lower()

    if value == "":
        return True

    for pattern in BAD_PATTERNS:
        if pattern in value:
            return True

    if len(value) <= 2:
        return True

    if re.fullmatch(r"[\W_]+", value):
        return True

    return False


def canonical_identity(name, email):
    name = clean_text(name)
    email = extract_email(email)

    if email in EMAIL_MAP:
        return EMAIL_MAP[email]

    name_norm = name.lower().strip()

    if name_norm in NAME_MAP:
        return NAME_MAP[name_norm]

    if is_bad_identity(name) and not email:
        return "Unknown"

    if name and not is_bad_identity(name):
        return name

    if email and not is_bad_identity(email):
        return email

    return "Unknown"


def parse_identity(raw):
    raw = clean_text(raw)

    email = extract_email(raw)
    name = extract_name(raw)

    if not name and email:
        name = email

    person = canonical_identity(name, email)

    return person, email, name


def load_threads():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    os.makedirs("data/clean", exist_ok=True)

    rows = []

    for record in load_threads():
        data = record.get("data", {})
        thread = data.get("thread", {})
        messages = thread.get("messages", [])

        for message in messages:
            message_id = message.get("id")
            doc_id = message.get("doc_id")
            subject = message.get("subject", "")
            sent_at = message.get("sent_at", "")

            sender_name = message.get("sender_name", "")
            sender_email = message.get("sender_email", "")

            source = canonical_identity(sender_name, sender_email)
            source_email = extract_email(sender_email)

            if source == "Unknown":
                continue

            recipient_groups = [
                ("to", message.get("to_recipients", [])),
                ("cc", message.get("cc_recipients", [])),
                ("bcc", message.get("bcc_recipients", [])),
            ]

            for recipient_type, recipients in recipient_groups:
                if not recipients:
                    continue

                for raw_recipient in recipients:
                    target, target_email, target_name = parse_identity(raw_recipient)

                    if target == "Unknown":
                        continue

                    if source == target:
                        continue

                    rows.append({
                        "message_id": message_id,
                        "doc_id": doc_id,
                        "sent_at": sent_at,
                        "subject": subject,
                        "source": source,
                        "source_email": source_email,
                        "target": target,
                        "target_email": target_email,
                        "target_name": target_name,
                        "recipient_type": recipient_type,
                    })

    df = pd.DataFrame(rows)

    if df.empty:
        print("Aucune relation trouvée.")
        return

    df = df.drop_duplicates(
        subset=["message_id", "source", "target", "recipient_type"]
    )

    df.to_csv(OUTPUT_RECIPIENTS, index=False, encoding="utf-8-sig")

    edges = (
        df.groupby(["source", "target"], dropna=False)
          .agg(
              weight=("message_id", "nunique"),
              first_date=("sent_at", "min"),
              last_date=("sent_at", "max"),
              recipient_types=("recipient_type", lambda x: ",".join(sorted(set(x))))
          )
          .reset_index()
          .sort_values("weight", ascending=False)
    )

    edges.to_csv(OUTPUT_EDGES, index=False, encoding="utf-8-sig")

    sent_counts = (
        df.groupby("source")
          .agg(sent_count=("message_id", "nunique"))
          .reset_index()
          .rename(columns={"source": "person_id"})
    )

    received_counts = (
        df.groupby("target")
          .agg(received_count=("message_id", "nunique"))
          .reset_index()
          .rename(columns={"target": "person_id"})
    )

    nodes = pd.merge(sent_counts, received_counts, on="person_id", how="outer")
    nodes["sent_count"] = nodes["sent_count"].fillna(0).astype(int)
    nodes["received_count"] = nodes["received_count"].fillna(0).astype(int)
    nodes["total_count"] = nodes["sent_count"] + nodes["received_count"]

    nodes = nodes.sort_values("total_count", ascending=False)

    nodes.to_csv(OUTPUT_NODES, index=False, encoding="utf-8-sig")

    print("Fichier créé :", OUTPUT_RECIPIENTS)
    print("Fichier créé :", OUTPUT_EDGES)
    print("Fichier créé :", OUTPUT_NODES)

    print("\nTop 30 des relations :")
    print(edges.head(30).to_string(index=False))

    print("\nTop 30 des nœuds du graphe :")
    print(nodes.head(30).to_string(index=False))


if __name__ == "__main__":
    main()