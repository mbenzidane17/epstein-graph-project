import os
import json
import pandas as pd
import requests

EMAIL_INDEX_FILE = "data/clean/jmail_email_index.csv"
OUTPUT_DIR = "data/raw/thread_detail_tests"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://jmail.world/",
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(EMAIL_INDEX_FILE)

    # On teste quelques emails envoyés par Epstein
    sample = df[
        df["sender_raw"].astype(str).str.contains("Epstein", case=False, na=False)
    ].head(10)

    if sample.empty:
        sample = df.head(10)

    print("Emails testés :")
    print(sample[["email_id", "subject", "sender_raw"]].to_string(index=False))

    for _, row in sample.iterrows():
        doc_id = row["email_id"]
        url = f"https://jmail.world/api/threads/{doc_id}"

        print("\n" + "=" * 80)
        print("Test doc_id :", doc_id)
        print("URL :", url)

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            print("Status code :", response.status_code)
            print("Content-Type :", response.headers.get("content-type"))

            output_path = os.path.join(OUTPUT_DIR, f"{doc_id}.txt")

            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()

                json_path = os.path.join(OUTPUT_DIR, f"{doc_id}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print("JSON sauvegardé :", json_path)

                print("\nClés principales :")
                if isinstance(data, dict):
                    print(list(data.keys()))

                print("\nAperçu JSON :")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])

            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response.text)

                print("Réponse texte sauvegardée :", output_path)
                print("\nAperçu texte :")
                print(response.text[:1000])

        except Exception as e:
            print("Erreur :", e)


if __name__ == "__main__":
    main()