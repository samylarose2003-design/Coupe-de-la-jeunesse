import json
import os
import shutil
from datetime import datetime

from models import Joueur, Equipe, Match


class Storage:
    def __init__(self, chemin="data.json"):
        self.chemin = chemin

    def charger(self):
        """Retourne un dict {'equipes': [...], 'matchs': [...], 'historique': [...]}."""
        if not os.path.exists(self.chemin):
            return {"equipes": [], "matchs": [], "historique": []}

        try:
            with open(self.chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            backup = f"{self.chemin}.corrompu.{datetime.now():%Y%m%d_%H%M%S}"
            try:
                shutil.copy(self.chemin, backup)
                print(f" Fichier invalide. Copie de secours : {backup}")
            except OSError:
                print("Fichier invalide et copie impossible.")
            return {"equipes": [], "matchs": [], "historique": []}

        # Validation structurelle
        if not isinstance(data, dict):
            print("Structure JSON invalide. Réinitialisation en mémoire.")
            return {"equipes": [], "matchs": [], "historique": []}

        equipes = []
        for d in data.get("equipes", []):
            try:
                equipes.append(Equipe.from_dict(d))
            except (KeyError, ValueError) as e:
                print(f" Équipe ignorée (données invalides) : {e}")

        matchs = []
        for d in data.get("matchs", []):
            try:
                matchs.append(Match.from_dict(d))
            except (KeyError, ValueError) as e:
                print(f" Match ignoré (données invalides) : {e}")

        return {
            "equipes": equipes,
            "matchs": matchs,
            "historique": data.get("historique", []),
        }

    def sauvegarder(self, equipes, matchs, historique):
        payload = {
            "equipes": [e.to_dict() for e in equipes],
            "matchs": [m.to_dict() for m in matchs],
            "historique": historique,
        }
        tmp = self.chemin + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.chemin)  # écriture atomique