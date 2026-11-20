from collections import defaultdict
from datetime import datetime

from models import Equipe, Joueur, Match

tournoi_name = "LIGUE DE LA JEUNESSE"

class Tournoi:
    # Barème
    POINTS_VICTOIRE = 3
    POINTS_NUL = 1
    POINTS_DEFAITE = 0

    def __init__(self, storage):
        self.storage = storage
        data = storage.charger()
        self.equipes = data["equipes"]
        self.matchs = data["matchs"]
        self.historique = data["historique"]

    # ---------- Persistance ----------
    def sauvegarder(self):
        self.storage.sauvegarder(self.equipes, self.matchs, self.historique)

    def _log(self, action):
        self.historique.append({
            "date": datetime.now().isoformat(timespec="seconds"),
            "action": action,
        })

    # ---------- Utilitaires ----------
    def _trouver_equipe(self, equipe_id):
        for e in self.equipes:
            if e.id == equipe_id:
                return e
        return None

    def _trouver_match(self, match_id):
        for m in self.matchs:
            if m.id == match_id:
                return m
        return None

    # ---------- Équipes / Joueurs ----------
    def inscrire_equipe(self, nom):
        nom = nom.strip()
        if not nom:
            raise ValueError("Le nom de l'équipe ne peut pas être vide.")
        if any(e.nom.lower() == nom.lower() for e in self.equipes):
            raise ValueError(f"Une équipe nommée '{nom}' existe déjà.")
            print("Appuyez sur ENTER pour continuer")
            input()

        equipe = Equipe(nom)
        self.equipes.append(equipe)
        self._log(f"Inscription équipe '{nom}' (id={equipe.id})")
        self.sauvegarder()
        return equipe

    def ajouter_joueur(self, equipe_id, nom, numero, poste=""):
        equipe = self._trouver_equipe(equipe_id)
        if not equipe:
            raise ValueError("Équipe introuvable.")
        # On crée le joueur seulement si l'ajout est autorisé
        # (vérification préalable pour ne pas consommer d'id en cas d'échec)
        if len(equipe.joueurs) >= Equipe.MAX_JOUEURS:
            raise ValueError(f"Effectif maximum atteint ({Equipe.MAX_JOUEURS}).")
        if any(j.numero == int(numero) for j in equipe.joueurs):
            raise ValueError(f"Le numéro {numero} est déjà pris dans cette équipe.")
        joueur = Joueur(nom, numero, poste)
        equipe.ajouter_joueur(joueur)
        self._log(f"Ajout joueur '{nom}' #{numero} à {equipe.nom}")
        self.sauvegarder()
        return joueur

    # ---------- Calendrier ----------
    def generer_calendrier(self, forcer=False):
        if len(self.equipes) < 2:
            raise ValueError("Il faut au moins 2 équipes pour générer un calendrier.")

        nb_joues = sum(1 for m in self.matchs if m.joue)
        if self.matchs and not forcer:
            msg = "Un calendrier existe déjà."
            if nb_joues:
                msg += f" {nb_joues} match(s) joué(s) seront PERDUS."
            raise ValueError(msg + " Utilisez 'forcer' pour régénérer.")

        equipes = list(self.equipes)
        n = len(equipes)
        if n % 2 == 1:
            equipes.append(None)   # bye virtuel
            n += 1

        nb_rounds = n - 1
        matchs_par_round = n // 2
        nouveaux_matchs = []

        Match._next_id = 1   # ✅ IDs repartent de 1

        indices = list(range(n))
        for r in range(nb_rounds):
            creneau = r + 1
            for i in range(matchs_par_round):
                a = indices[i]
                b = indices[n - 1 - i]
                eq_a = equipes[a]        # ✅ on récupère l'équipe
                eq_b = equipes[b]
                if eq_a is None or eq_b is None:   # ✅ on teste l'équipe
                    continue
                m = Match(eq_a.id, eq_b.id, creneau=creneau)
                nouveaux_matchs.append(m)
            # rotation : fixe le 1er, tourne les autres
            indices = [indices[0]] + [indices[-1]] + indices[1:-1]

        anciens_joues = nb_joues
        self.matchs = nouveaux_matchs

        if anciens_joues:
            self._log(
                f"Régénération calendrier : {anciens_joues} score(s) effacé(s), "
                f"{len(nouveaux_matchs)} nouveaux matchs (IDs réinitialisés)"
            )
        else:
            self._log(f"Génération calendrier : {len(nouveaux_matchs)} matchs")

        self.sauvegarder()
        return nouveaux_matchs

    # ---------- Scores ----------
    def enregistrer_score(self, match_id, buts_a, buts_b):
        match = self._trouver_match(match_id)
        if not match:
            raise ValueError("Match introuvable.")
        buts_a = int(buts_a)
        buts_b = int(buts_b)
        if buts_a < 0 or buts_b < 0:
            raise ValueError("Les scores doivent être positifs.")
        ancien = (match.buts_a, match.buts_b)
        match.enregistrer_score(buts_a, buts_b)
        self._log(
            f"Score match#{match_id} : {ancien} -> ({buts_a}-{buts_b})"
        )
        self.sauvegarder()

    def corriger_score(self, match_id, buts_a, buts_b):
        match = self._trouver_match(match_id)
        if not match:
            raise ValueError("Match introuvable.")
        if not match.joue:
            raise ValueError("Ce match n'a pas encore de score à corriger.")
        buts_a = int(buts_a)
        buts_b = int(buts_b)
        if buts_a < 0 or buts_b < 0:
            raise ValueError("Les scores doivent être positifs.")
        ancien = (match.buts_a, match.buts_b)
        match.enregistrer_score(buts_a, buts_b)
        self._log(
            f"Correction match#{match_id} : {ancien} -> ({buts_a}-{buts_b})"
        )
        self.sauvegarder()

    # ---------- Classement ----------
    def calculer_classement(self):
        stats = {}
        for e in self.equipes:
            stats[e.id] = {
                "equipe": e,
                "joues": 0,
                "gagnes": 0,
                "nuls": 0,
                "perdus": 0,
                "buts_pour": 0,
                "buts_contre": 0,
                "points": 0,
            }

        for m in self.matchs:
            if not m.joue:
                continue
            if m.equipe_a_id not in stats or m.equipe_b_id not in stats:
                continue
            a = stats[m.equipe_a_id]
            b = stats[m.equipe_b_id]
            a["joues"] += 1
            b["joues"] += 1
            a["buts_pour"] += m.buts_a
            a["buts_contre"] += m.buts_b
            b["buts_pour"] += m.buts_b
            b["buts_contre"] += m.buts_a
            if m.buts_a > m.buts_b:
                a["gagnes"] += 1
                a["points"] += self.POINTS_VICTOIRE
                b["perdus"] += 1
                b["points"] += self.POINTS_DEFAITE
            elif m.buts_a < m.buts_b:
                b["gagnes"] += 1
                b["points"] += self.POINTS_VICTOIRE
                a["perdus"] += 1
                a["points"] += self.POINTS_DEFAITE
            else:
                a["nuls"] += 1
                b["nuls"] += 1
                a["points"] += self.POINTS_NUL
                b["points"] += self.POINTS_NUL

        classement = list(stats.values())
        for c in classement:
            c["diff"] = c["buts_pour"] - c["buts_contre"]

        # Tri : points > diff > buts_pour > nom
        classement.sort(
            key=lambda c: (
                -c["points"],
                -c["diff"],
                -c["buts_pour"],
                c["equipe"].nom.lower(),
            )
        )

        # Détection des égalités persistantes (même points, diff, buts_pour)
        egalites = []
        for i in range(len(classement) - 1):
            c1, c2 = classement[i], classement[i + 1]
            if (
                c1["points"] == c2["points"]
                and c1["diff"] == c2["diff"]
                and c1["buts_pour"] == c2["buts_pour"]
            ):
                egalites.append((c1["equipe"].nom, c2["equipe"].nom))

        return classement, egalites

    def matchs_restants(self):
        return [m for m in self.matchs if not m.joue]

    def matchs_a_venir_equipe(self, equipe_id):
        return [
            m for m in self.matchs
            if not m.joue and equipe_id in (m.equipe_a_id, m.equipe_b_id)
        ]

    def rechercher_equipe(self, terme):
        terme = terme.lower()
        return [e for e in self.equipes if terme in e.nom.lower()]