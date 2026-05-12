import pandas as pd
import re
import os

INPUT_FILE = "data/clean/jmail_email_index.csv"
OUTPUT_FILE = "data/clean/jmail_email_index_clean.csv"


def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Nettoyage des guillemets parasites
    value = value.strip('"').strip("'").strip()
    value = value.replace('""', '"')

    # Espaces multiples
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_email(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", value)
    if match:
        return match.group(0).lower()

    return ""


def clean_display_name(value):
    value = normalize_text(value)

    # Supprimer guillemets restants
    value = value.replace('"', "")

    # Supprimer points/tirets de fin
    value = re.sub(r"\s+-\s*$", "", value)
    value = re.sub(r"\.\s*$", "", value)

    # Cas "on behalf of" : on garde la personne représentée
    match = re.search(r"on behalf of\s+(.+)$", value, flags=re.IGNORECASE)
    if match:
        value = match.group(1).strip()

    value = re.sub(r"\s+", " ", value).strip()

    return value


def is_redacted_or_bad_identity(name, email):
    name_norm = normalize_text(name).lower()
    email_norm = normalize_email(email).lower()

    # Si on a un vrai email exploitable, ce n'est pas forcément mauvais
    if email_norm and "@" in email_norm and "redacted" not in email_norm:
        return False

    if name_norm == "":
        return True

    if name_norm in {"unknown", "nan", "none", "'", '"', '""'}:
        return True

    bad_keywords = [
        "redacted",
        "blacked out",
        "content is blacked out",
        "information obscured",
        "information redacted",
        "mailto:",
    ]

    for keyword in bad_keywords:
        if keyword in name_norm:
            return True

    # Si la valeur est composée principalement de blocs de censure
    if "█" in name_norm:
        return True

    # Identifiants trop courts / symboles seuls
    if len(name_norm) <= 2:
        return True

    if re.fullmatch(r"[\W_]+", name_norm):
        return True

    return False


def canonical_name(sender_name, sender_email):
    name = clean_display_name(sender_name)
    email = normalize_email(sender_email)

    # Si sender_email est vide mais sender_name contient un email
    if not email:
        email = normalize_email(sender_name)

    email_map = {
        "jeevacation@gmail.com": "Jeffrey Epstein",
        "jeeproject@yahoo.com": "Jeffrey Epstein",
        "ehbarak1@gmail.com": "Ehud Barak",
        "gmax1@ellmax.com": "Ghislaine Maxwell",
        "lesley@nysgllc.com": "Lesley Groff",
        "rkahn@nysgmail.com": "Richard Kahn",
    }

    if email in email_map:
        return email_map[email]

    if is_redacted_or_bad_identity(name, email):
        return "Unknown"

    name_norm = normalize_text(name).lower()

    name_map = {
        "jeffrey epstein": "Jeffrey Epstein",
        "jeffrey e.": "Jeffrey Epstein",
        "jeffrey e": "Jeffrey Epstein",
        "j. epstein": "Jeffrey Epstein",

        "gmax": "Ghislaine Maxwell",
        "g. max": "Ghislaine Maxwell",
        "ghislaine maxwell": "Ghislaine Maxwell",

        "rich kahn": "Richard Kahn",
        "richard kahn": "Richard Kahn",
        "rkahn": "Richard Kahn",

        "lesley groff": "Lesley Groff",

        "ehud barak": "Ehud Barak",
        "ehbarak": "Ehud Barak",
    }

    if name_norm in name_map:
        return name_map[name_norm]

    # Si on a un email inconnu mais propre, on peut garder l'email
    if email and "@" in email:
        return email

    return name


def main():
    os.makedirs("data/clean", exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    df["sender_name_norm"] = df["sender_name"].apply(clean_display_name)
    df["sender_email_norm"] = df.apply(
        lambda row: normalize_email(row["sender_email"]) or normalize_email(row["sender_name"]),
        axis=1
    )

    df["sender_canonical"] = df.apply(
        lambda row: canonical_name(row["sender_name"], row["sender_email"]),
        axis=1
    )

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"Fichier créé : {OUTPUT_FILE}")

    print("\nTop 30 des identités canoniques :")
    print(df["sender_canonical"].value_counts().head(30).to_string())

    print("\nNombre de Unknown :")
    print((df["sender_canonical"] == "Unknown").sum())


if __name__ == "__main__":
    main()