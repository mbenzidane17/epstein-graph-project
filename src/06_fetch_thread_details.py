import os
import json
import time
import argparse
import pandas as pd
import requests

INPUT_FILE = "data/clean/jmail_email_index.csv"
OUTPUT_FILE = "data/raw/thread_details.jsonl"
ERROR_FILE = "data/raw/thread_fetch_errors.csv"

API_URL = "https://jmail.world/api/threads/{doc_id}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://jmail.world/",
}


def load_done_doc_ids():
    done = set()

    if not os.path.exists(OUTPUT_FILE):
        return done

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                doc_id = record.get("doc_id")
                if doc_id:
                    done.add(doc_id)
            except Exception:
                continue

    return done


def fetch_thread(doc_id):
    url = API_URL.format(doc_id=doc_id)
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        return {
            "doc_id": doc_id,
            "status_code": response.status_code,
            "error": response.text[:500],
        }

    return {
        "doc_id": doc_id,
        "status_code": response.status_code,
        "data": response.json(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()

    os.makedirs("data/raw", exist_ok=True)

    df = pd.read_csv(INPUT_FILE)
    doc_ids = df["email_id"].dropna().astype(str).drop_duplicates().tolist()

    if args.limit:
        doc_ids = doc_ids[:args.limit]

    done = load_done_doc_ids()

    print("Nombre total à traiter :", len(doc_ids))
    print("Déjà récupérés :", len(done))

    errors = []

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for i, doc_id in enumerate(doc_ids, start=1):
            if doc_id in done:
                continue

            print(f"[{i}/{len(doc_ids)}] Fetch {doc_id}")

            try:
                record = fetch_thread(doc_id)

                if record.get("status_code") == 200:
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out.flush()
                else:
                    errors.append(record)

            except Exception as e:
                errors.append({
                    "doc_id": doc_id,
                    "status_code": None,
                    "error": str(e),
                })

            time.sleep(args.delay)

    if errors:
        pd.DataFrame(errors).to_csv(ERROR_FILE, index=False, encoding="utf-8-sig")
        print("Erreurs sauvegardées :", ERROR_FILE)

    print("Fichier JSONL créé :", OUTPUT_FILE)


if __name__ == "__main__":
    main()