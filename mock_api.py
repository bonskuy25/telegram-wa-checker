# mock_api.py
from flask import Flask, request, jsonify

app = Flask(__name__)

def classify_number(number: str):
    """
    Simple deterministic mock logic:
    - Jika angka terakhir adalah '0' -> not_registered
    - Jika angka terakhir ganjil -> no_bio
    - Jika angka terakhir genap (selain 0) -> with_bio (dan beri contoh bio)
    """
    if not number or not number[-1].isdigit():
        return {"status": "not_registered"}

    last = number[-1]
    if last == "0":
        return {"status": "not_registered"}
    elif last in "13579":
        return {"status": "no_bio"}
    else:
        # with bio example
        return {"status": "with_bio", "bio": "Sibuk bro, chat nanti ✌️"}

@app.route("/cekbio", methods=["POST"])
def cekbio():
    """
    Request JSON:
    { "number": "6281234567890" }

    Response examples:
    { "status": "with_bio", "bio": "..." }
    { "status": "no_bio" }
    { "status": "not_registered" }
    """
    data = request.get_json(force=True, silent=True) or {}
    number = data.get("number") or data.get("nomor") or ""
    result = classify_number(number)
    return jsonify(result)

@app.route("/cekbulk", methods=["POST"])
def cekbulk():
    """
    Request JSON:
    { "numbers": ["6281...", "6282...", ...] }

    Response:
    {
      "results": [
        {"number":"6281...","status":"with_bio","bio":"..."},
        ...
      ],
      "summary": {"total":3,"with_bio":1,"no_bio":1,"not_registered":1}
    }
    """
    data = request.get_json(force=True, silent=True) or {}
    numbers = data.get("numbers") or []
    results = []
    summary = {"total": 0, "with_bio": 0, "no_bio": 0, "not_registered": 0}
    for num in numbers:
        res = classify_number(num)
        entry = {"number": num, **res}
        results.append(entry)
        summary["total"] += 1
        if res["status"] == "with_bio":
            summary["with_bio"] += 1
        elif res["status"] == "no_bio":
            summary["no_bio"] += 1
        else:
            summary["not_registered"] += 1

    return jsonify({"results": results, "summary": summary})

if __name__ == "__main__":
    # Jalankan lokal: python mock_api.py
    # Akan jalan di http://127.0.0.1:5000/
    app.run(host="0.0.0.0", port=5000, debug=True)
