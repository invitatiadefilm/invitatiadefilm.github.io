#!/usr/bin/env python3
"""Genereaza pagina de invitatie + pagina gazdelor pentru un client.

Folosire:  python3 unelte/genereaza.py unelte/clienti/<slug>.json
Rezultat:  folderul /<slug>/ in radacina site-ului (index.html, raspunsuri/, config.js, stil.css)

Codul de acces al gazdelor NU sta aici: se trece doar in tabelul Google, foaia "Evenimente".
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

AICI = Path(__file__).resolve().parent
SITE = AICI.parent
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTKdSMhES1xyztQ9HhTc0U71WWKvoL7tEfAsmqt0hrertJ6jxMh056EwKImVfehBPX/exec"

ZILE = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
LUNI = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie",
        "august", "septembrie", "octombrie", "noiembrie", "decembrie"]

IMPLICIT = {
    "nunta": {
        "eyebrow": "Vă invităm la nunta noastră",
        "eveniment": "nuntă",
        "intrebare": "Veniți la nuntă?",
        "mesaj": "Un gând pentru miri",
        "pagina_gazde": "Pagina mirilor",
        "cal_titlu": "Nunta {titlu}",
        "descriere": "Vă invităm la nunta noastră. Vedeți invitația și confirmați prezența până pe {pana_la}.",
        "meniuri": ["Clasic", "Vegetarian", "Pește"],
        "meniu_nota": "Copiii primesc automat meniul pentru cei mici.",
    },
    "botez": {
        "eyebrow": "Vă invit cu drag la botezul meu",
        "eveniment": "botez",
        "intrebare": "Veniți la botez?",
        "mesaj": "Un gând pentru {titlu}",
        "pagina_gazde": "Pagina părinților",
        "cal_titlu": "Botez {titlu}",
        "descriere": "Vă invităm la botez. Vedeți invitația și confirmați prezența până pe {pana_la}.",
        "meniuri": ["Clasic", "Vegetarian"],
        "meniu_nota": "Copiii primesc automat meniul pentru cei mici.",
    },
    "aniversare": {
        "eyebrow": "Te invit la ziua mea!",
        "eveniment": "petrecere",
        "intrebare": "Veniți la petrecere?",
        "mesaj": "Un gând pentru {titlu}",
        "pagina_gazde": "Pagina părinților",
        "cal_titlu": "Ziua lui {titlu}",
        "descriere": "Te invit la ziua mea! Vezi invitația și confirmă până pe {pana_la}.",
        "meniuri": [],
        "meniu_nota": "",
    },
}
COMUN = {
    "da": "Da, venim cu drag",
    "da_sub": "Ne vedem pe {zi_luna}",
    "nu": "Din păcate, nu putem",
    "nu_sub": "Vă trimitem gânduri bune",
    "multumire_da": "Confirmarea a ajuns la noi. Ne vedem pe {zi_luna}, abia așteptăm!",
    "multumire_nu": "Ne pare rău că nu puteți ajunge. Vă mulțumim că ne-ați anunțat.",
}


def utc(iso):
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def favicon(titlu):
    parti = [p.strip() for p in titlu.split("&")]
    txt = "&amp;".join(p[0] for p in parti if p) if len(parti) > 1 else titlu[:1]
    size = 30 if len(parti) > 1 else 36
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='#2E4536'/>"
           f"<text x='32' y='43' text-anchor='middle' font-family='Georgia,serif' font-style='italic' font-size='{size}' fill='#F5F6F1'>{txt}</text></svg>")
    return "data:image/svg+xml," + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23").replace("&", "%26")


def main(cale):
    c = json.loads(Path(cale).read_text(encoding="utf-8"))
    tip = c.get("tip", "nunta")
    d = dict(COMUN, **IMPLICIT[tip])
    d.update({k: v for k, v in c.items() if k != "rsvp"})
    rsvp_in = c.get("rsvp", {})

    start = datetime.fromisoformat(c["start"])
    zi_luna = f"{start.day} {LUNI[start.month - 1]}"
    fmt = {
        "titlu": c["titlu"],
        "zi_luna": zi_luna,
        "pana_la": rsvp_in.get("pana_la", ""),
    }

    def f(v):
        return v.format(**fmt) if isinstance(v, str) else v

    rsvp = {k: f(rsvp_in.get(k, d.get(k))) for k in
            ["intrebare", "da", "da_sub", "nu", "nu_sub", "mesaj", "meniuri", "meniu_nota"]}
    rsvp["pana_la"] = rsvp_in.get("pana_la", "")
    rsvp["cazare"] = rsvp_in.get("cazare")

    parti = [p.strip() for p in c["titlu"].split("&")]
    if len(parti) == 2:
        nume_h1 = Markup(f'{escape(parti[0])} <span class="iv-amp">&amp;</span> {escape(parti[1])}')
    else:
        nume_h1 = c["titlu"]

    program = c.get("program", [])
    cal_loc = c.get("cal_loc") or (program[-1]["loc"][-1] if program else "")
    cal_det = c.get("cal_detalii") or ", ".join(f'{p["titlu"]} la {p["ora"]}' for p in program) + "."

    ctx = dict(d)
    ctx.update({
        "slug": c["slug"],
        "nume_h1": nume_h1,
        "data_text": c.get("data_text") or f"{ZILE[start.weekday()]}, {zi_luna} {start.year}",
        "data_titlu": f"{zi_luna} {start.year}",
        "data_scurta": start.strftime("%d.%m.%Y"),
        "descriere": f(d["descriere"]),
        "eyebrow": f(d["eyebrow"]),
        "favicon": favicon(c["titlu"]),
        "rsvp": rsvp,
        "meniuri": rsvp["meniuri"],
        "cazare": rsvp["cazare"],
        "pagina_gazde": f(d["pagina_gazde"]),
        "demo": c.get("demo", False),
        "noindex": c.get("noindex", False),
        "nota_demo": c.get("nota_demo", ""),
        "cod_demo": c.get("cod_demo", ""),
        "og": c.get("og") or c["poster"],
    })

    env = Environment(loader=FileSystemLoader(AICI / "sablon"), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    out = SITE / c["slug"]
    (out / "raspunsuri").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(env.get_template("index.html").render(**ctx), encoding="utf-8")
    (out / "raspunsuri" / "index.html").write_text(env.get_template("raspunsuri.html").render(**ctx), encoding="utf-8")
    shutil.copyfile(AICI / "sablon" / "stil.css", out / "stil.css")

    iv = {
        "ev": c["slug"],
        "start": c["start"],
        "meniuri": rsvp["meniuri"] or [],
        "cazare": bool(rsvp["cazare"]),
        "multumire_da": f(d["multumire_da"]),
        "multumire_nu": f(d["multumire_nu"]),
        "cal": {
            "titlu": f(d["cal_titlu"]),
            "start": utc(c["start"]),
            "sfarsit": utc(c.get("sfarsit") or c["start"]),
            "detalii": cal_det,
            "loc": cal_loc,
        },
    }
    (out / "config.js").write_text(
        "// Generat de unelte/genereaza.py. Nu edita de mana: modifica fisierul din unelte/clienti/ si genereaza din nou.\n"
        f"window.IV_SCRIPT_URL = {json.dumps(SCRIPT_URL)};\n"
        f"window.IV = {json.dumps(iv, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8")
    print(f"Gata: {out.relative_to(SITE)}/  ->  https://invitatiadefilm.github.io/{c['slug']}/")


if __name__ == "__main__":
    main(sys.argv[1])
