class Joueur:
    _next_id = 1

    def __init__(self, nom, numero, poste="", joueur_id=None):
        if joueur_id is not None:
            self._id = joueur_id
            Joueur._next_id = max(Joueur._next_id, joueur_id + 1)
        else:
            self._id = Joueur._next_id
            Joueur._next_id += 1
        self._nom = nom.strip()
        self._numero = int(numero)
        self._poste = poste.strip()

    # Getters / Setters
    @property
    def id(self):
        return self._id

    @property
    def nom(self):
        return self._nom

    @property
    def numero(self):
        return self._numero

    @property
    def poste(self):
        return self._poste

    def to_dict(self):
        return {
            "id": self._id,
            "nom": self._nom,
            "numero": self._numero,
            "poste": self._poste,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["nom"], d["numero"], d.get("poste", ""), d["id"])

    def __repr__(self):
        return f"#{self._numero} {self._nom}"


class Equipe:
    _next_id = 1
    MAX_JOUEURS = 11
    MIN_JOUEURS = 5

    def __init__(self, nom, equipe_id=None, joueurs=None):
        if equipe_id is not None:
            self._id = equipe_id
            Equipe._next_id = max(Equipe._next_id, equipe_id + 1)
        else:
            self._id = Equipe._next_id
            Equipe._next_id += 1
        self._nom = nom.strip()
        self._joueurs = joueurs if joueurs is not None else []

    @property
    def id(self):
        return self._id

    @property
    def nom(self):
        return self._nom

    @property
    def joueurs(self):
        return list(self._joueurs)

    def ajouter_joueur(self, joueur):
        if len(self._joueurs) >= Equipe.MAX_JOUEURS:
            raise ValueError(
                f"L'équipe {self._nom} a déjà {Equipe.MAX_JOUEURS} joueurs (maximum)."
            )
        if any(j.numero == joueur.numero for j in self._joueurs):
            raise ValueError(
                f"Le numéro {joueur.numero} est déjà utilisé dans {self._nom}."
            )
        self._joueurs.append(joueur)

    def retirer_joueur(self, joueur_id):
        for j in self._joueurs:
            if j.id == joueur_id:
                self._joueurs.remove(j)
                return True
        return False

    def effectif_valide(self):
        return Equipe.MIN_JOUEURS <= len(self._joueurs) <= Equipe.MAX_JOUEURS

    def to_dict(self):
        return {
            "id": self._id,
            "nom": self._nom,
            "joueurs": [j.to_dict() for j in self._joueurs],
        }

    @classmethod
    def from_dict(cls, d):
        joueurs = [Joueur.from_dict(j) for j in d.get("joueurs", [])]
        return cls(d["nom"], d["id"], joueurs)

    def __repr__(self):
        return f"{self._nom} ({len(self._joueurs)} joueurs)"


class Match:
    """Rencontre entre deux équipes."""
    _next_id = 1

    def __init__(self, equipe_a_id, equipe_b_id, match_id=None,
                 buts_a=None, buts_b=None, creneau=None, joue=False):
        if match_id is not None:
            self._id = match_id
            Match._next_id = max(Match._next_id, match_id + 1)
        else:
            self._id = Match._next_id
            Match._next_id += 1
        self._equipe_a_id = equipe_a_id
        self._equipe_b_id = equipe_b_id
        self._buts_a = buts_a
        self._buts_b = buts_b
        self._creneau = creneau
        self._joue = joue

    @property
    def id(self):
        return self._id

    @property
    def equipe_a_id(self):
        return self._equipe_a_id

    @property
    def equipe_b_id(self):
        return self._equipe_b_id

    @property
    def buts_a(self):
        return self._buts_a

    @property
    def buts_b(self):
        return self._buts_b

    @property
    def creneau(self):
        return self._creneau

    @property
    def joue(self):
        return self._joue

    def enregistrer_score(self, buts_a, buts_b, creneau=None):
        if buts_a < 0 or buts_b < 0:
            raise ValueError("Les scores ne peuvent pas être négatifs.")
        self._buts_a = int(buts_a)
        self._buts_b = int(buts_b)
        self._joue = True
        if creneau is not None:
            self._creneau = creneau

    def to_dict(self):
        return {
            "id": self._id,
            "equipe_a_id": self._equipe_a_id,
            "equipe_b_id": self._equipe_b_id,
            "buts_a": self._buts_a,
            "buts_b": self._buts_b,
            "creneau": self._creneau,
            "joue": self._joue,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["equipe_a_id"],
            d["equipe_b_id"],
            d["id"],
            d.get("buts_a"),
            d.get("buts_b"),
            d.get("creneau"),
            d.get("joue", False),
        )

    def __repr__(self):
        return f"Match#{self._id} [{self._equipe_a_id} vs {self._equipe_b_id}]"