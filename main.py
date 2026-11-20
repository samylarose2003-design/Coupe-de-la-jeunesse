import sys
import os
from storage import Storage
from tournoi import Tournoi

tournoi_name = "LIGUE DE LA JEUNESSE"



def clear_screen():
  print("\033[H\033[J", end="")




def afficher_menu():
    print("\033[H\033[J", end="")
    print("\n" + "=" * 55)
    print(f"{tournoi_name} - Menu Principal")
    print("=" * 55)
    print(" 1. Inscrire une équipe")
    print(" 2. Ajouter un joueur à une équipe")
    print(" 3. Lister les équipes et effectifs")
    print(" 4. Générer le calendrier")
    print(" 5. Afficher le calendrier")
    print(" 6. Enregistrer un score")
    print(" 7. Corriger un score")
    print(" 8. Afficher le classement")
    print(" 9. Afficher les matchs restants")
    print("10. Statistiques d'une équipe")
    print("11. Rechercher une équipe")
    print("12. Afficher l'historique")
    print(" 0. Quitter")
    print("=" * 55)


def demander_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  ❌ Entrée invalide, entrez un nombre entier.")


def menu_equipes(tournoi):
    print("\n--- ÉQUIPES ---")
    if not tournoi.equipes:
        print("Aucune équipe inscrite.")
        return
    for e in tournoi.equipes:
        etat = "✅" if e.effectif_valide() else "⚠"
        print(f" [{e.id}] {etat} {e.nom} — {len(e.joueurs)} joueurs")
        for j in e.joueurs:
            poste = f" ({j.poste})" if j.poste else ""
            print(f"      #{j.numero} {j.nom}{poste}")


def menu_classement(tournoi):
    classement, egalites = tournoi.calculer_classement()
    print("\n\t\t\t\tCLASSEMENT\t\t\t\n")
    print(f"{'Pos':<4}{'Équipe':<20}{'Pts':<5}{'J':<4}{'G':<4}{'N':<4}{'P':<4}"
          f"{'BP':<5}{'BC':<5}{'Diff':<6}")
    print("-" * 65)
    for i, c in enumerate(classement, 1):
        print(f"{i:<4}{c['equipe'].nom:<20}{c['points']:<5}{c['joues']:<4}"
              f"{c['gagnes']:<4}{c['nuls']:<4}{c['perdus']:<4}"
              f"{c['buts_pour']:<5}{c['buts_contre']:<5}{c['diff']:<6}")
    if egalites:
        print("\n Égalités persistantes (mêmes pts, diff, BP) :")
        for a, b in egalites:
            print(f"   - {a} / {b}")


def menu_calendrier(tournoi):
    if not tournoi.matchs:
        print("Aucun calendrier généré.")
        return
    from collections import defaultdict
    par_creneau = defaultdict(list)
    for m in tournoi.matchs:
        par_creneau[m.creneau or 0].append(m)
    for c in sorted(par_creneau):
        print(f"\nCréneau {c}")
        for m in par_creneau[c]:
            eq_a = tournoi._trouver_equipe(m.equipe_a_id)
            eq_b = tournoi._trouver_equipe(m.equipe_b_id)
            if m.joue:
                statut = f"{m.buts_a} - {m.buts_b}"
            else:
                statut = "à jouer"
            print(f"   Match#{m.id} : {eq_a.nom} vs {eq_b.nom}  [{statut}]")


def menu_matchs_restants(tournoi):
    restants = tournoi.matchs_restants()
    if not restants:
        print("Tous les matchs ont été joués 🎉")
        return
    print(f"\n--- {len(restants)} MATCHS RESTANTS ---")
    for m in restants:
        eq_a = tournoi._trouver_equipe(m.equipe_a_id)
        eq_b = tournoi._trouver_equipe(m.equipe_b_id)
        print(f"  Match#{m.id} (C{m.creneau}) : {eq_a.nom} vs {eq_b.nom}")


def menu_stats_equipe(tournoi):
    if not tournoi.equipes:
        print("Aucune équipe.")
        return
    for e in tournoi.equipes:
        print(f"  [{e.id}] {e.nom}")
    eid = demander_int("ID équipe : ")
    equipe = tournoi._trouver_equipe(eid)
    if not equipe:
        print("❌ Équipe introuvable.")
        return
    classement, _ = tournoi.calculer_classement()
    stats = next((c for c in classement if c["equipe"].id == eid), None)
    print(f"\n\t\t\t\tSTATISTIQUES {equipe.nom}\t\t\t\n")
    print(f"Effectif : {len(equipe.joueurs)} joueurs\n")
    if stats:
        #print(f"Points : {stats['points']} | Matchs joués : {stats['joues']} | Gagnés : {stats['gagnes']} | Nuls : {stats['nuls']} | Perdus : {stats['perdus']} | BP : {stats['buts_pour']} | BC : {stats['buts_contre']} | Diff : {stats['diff']}")
        
        print("Points\t | Matchs joués\t | Gagnés\t | Nuls\t | Perdus\t | BP\t | BC\t | Diff")
        print(f"{stats['points']}\t | {stats['joues']}\t\t | {stats['gagnes']}\t\t | {stats['nuls']}\t | {stats['perdus']}\t\t | {stats['buts_pour']}\t | {stats['buts_contre']}\t | {stats['diff']}")
        
    a_venir = tournoi.matchs_a_venir_equipe(eid)
    print(f"\nMatchs restants : {len(a_venir)}\n")
    for m in a_venir:
        adversaire_id = m.equipe_b_id if m.equipe_a_id == eid else m.equipe_a_id
        adv = tournoi._trouver_equipe(adversaire_id)
        print(f"   vs {adv.nom} (créneau {m.creneau})")



def main():
    storage = Storage("data.json")
    tournoi = Tournoi(storage)

    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        try:
            if choix == "1":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Inscription Equipe")
                print("=" * 55)

                nom = input("Nom de l'équipe : ")
                eq = tournoi.inscrire_equipe(nom)
                print(f"✅ Équipe '{eq.nom}' inscrite (id={eq.id}) avec succes.")
                print("Appuyez sur ENTER pour continuer")
                input()
                print("\033[H\033[J", end="")

            elif choix == "2":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Inscription Joueur")
                print("=" * 55)

                if not tournoi.equipes:
                    print("❌ Inscrivez d'abord une équipe.")
                    continue
                for e in tournoi.equipes:
                    print(f"  [{e.id}] {e.nom}")
                eid = demander_int("\nID équipe : ")
                nom = input("Nom du joueur : ")
                num = demander_int("Numéro : ")
                poste = input("\nPoste du joueur :\n[1]: Gardien de but\n[2]: Defenseur\n[3]: Milieu\n[4]: Attaquant\n Choix (entre 1 a 4) : ")
                poste = int(poste)

                if poste == 1:
                    poste = "Gardien de but"
                elif poste == 2:
                    poste = "Defenseur"
                elif poste == 3:
                    poste = "Milieu"
                elif poste == 4:
                    poste = "Attaquant"
                j = tournoi.ajouter_joueur(eid, nom, num, poste)
                print(f"✅ Joueur {j.nom} ajouté.")
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "3":
                menu_equipes(tournoi)
                print("Appuyez sur ENTER pour continuer")
                input()

    
            elif choix == "4":
                if tournoi.matchs:
                    nb_joues = sum(1 for m in tournoi.matchs if m.joue)
                    print(f"\n⚠ Un calendrier existe ({len(tournoi.matchs)} matchs, "
                        f"{nb_joues} joués).")
                    print("  Régénérer va EFFACER tous les matchs et tous les scores.")
                    rep = input("  Confirmer la régénération ? (o/n) : ").strip().lower()
                    if rep != "o":
                        print("Régénération annulée.")
                        continue
                tournoi.generer_calendrier(forcer=True)
                print(f"✅ {len(tournoi.matchs)} matchs générés (scores réinitialisés).")
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "5":
                menu_calendrier(tournoi)
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "6":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Liste des matchs")
                print("=" * 55)

                if not tournoi.matchs:
                    print("❌ Générez d'abord le calendrier.")
                    continue

                # Affichage initial de tous les matchs
                for m in tournoi.matchs:
                    eq_a = tournoi._trouver_equipe(m.equipe_a_id)
                    eq_b = tournoi._trouver_equipe(m.equipe_b_id)
                    statut = f"{m.buts_a} - {m.buts_b}" if m.joue else "à jouer"
                    print(f"   Match#{m.id} : {eq_a.nom}\t\tvs\t{eq_b.nom}\t[{statut}]")

                # ✅ Boucle de saisie : on continue TANT QUE l'utilisateur répond 'o'
                while True:
                    mid = demander_int("\nID du match (0 pour terminer) : ")

                    # ✅ Sortie propre : taper 0 arrête la saisie
                    if mid == 0:
                        print("Fin de la saisie des scores.")
                        break

                    match_choisi = tournoi._trouver_match(mid)
                    if not match_choisi:
                        print(f"❌ Aucun match avec l'ID {mid}. Réessayez.")
                        continue

                    eq_a = tournoi._trouver_equipe(match_choisi.equipe_a_id)
                    eq_b = tournoi._trouver_equipe(match_choisi.equipe_b_id)

                    print(f"\nMatch#{match_choisi.id} : {eq_a.nom} vs {eq_b.nom}")
                    if match_choisi.joue:
                        print(f"   Score actuel : {match_choisi.buts_a} - {match_choisi.buts_b}")

                    ba = demander_int(f"Nombre de buts de {eq_a.nom} : ")
                    bb = demander_int(f"Nombre de buts de {eq_b.nom} : ")

                    tournoi.enregistrer_score(mid, ba, bb)
                    print(f"✅ Score enregistré : {eq_a.nom} [{ba} - {bb}] {eq_b.nom}")

                    # ✅ On redemande explicitement après CHAQUE saisie
                    rep = input("Saisir un autre score ? (o/n) : ").strip().lower()
                    if rep != "o":
                        print("Fin de la saisie des scores.")
                        break
                    
                    print("Appuyez sur ENTER pour continuer")
                    input()
      
                    
            elif choix == "7":
                if not tournoi.matchs:
                    print("❌ Aucun match.")
                    continue

                menu_calendrier(tournoi)

                mid = demander_int("\n\nID match à corriger : ")

                # ✅ On récupère le match choisi
                match_choisi = tournoi._trouver_match(mid)
                if not match_choisi:
                    print(f"❌ Aucun match avec l'ID {mid}.")
                    print("Appuyez sur ENTER pour continuer")
                    input()
                    continue

                if not match_choisi.joue:
                    print(f"❌ Le match#{mid} n'a pas encore de score. Utilisez le menu 6.")
                    print("Appuyez sur ENTER pour continuer")
                    input()
                    continue

                # ✅ Équipes du match choisi
                eq_a = tournoi._trouver_equipe(match_choisi.equipe_a_id)
                eq_b = tournoi._trouver_equipe(match_choisi.equipe_b_id)

                print(f"\nMatch#{match_choisi.id} : {eq_a.nom} {match_choisi.buts_a} - "
                    f"{match_choisi.buts_b} {eq_b.nom}")

                ba = demander_int(f"Nouveaux buts {eq_a.nom} : ")
                bb = demander_int(f"Nouveaux buts {eq_b.nom} : ")

                tournoi.corriger_score(mid, ba, bb)
                print(f"✅ Score corrigé : {eq_a.nom} [{ba} - {bb}] {eq_b.nom}")

                print("Appuyez sur ENTER pour continuer")
                input()

            elif choix == "8":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Classement")
                print("=" * 55)
                menu_classement(tournoi)
                print("\nAppuyez sur ENTER pour continuer")
                input()


            elif choix == "9":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Matchs restants")
                print("=" * 55)

                menu_matchs_restants(tournoi)
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "10":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Statistiques Equipes")
                print("=" * 55)

                menu_stats_equipe(tournoi)
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "11":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Recherche Equipes")
                print("=" * 55)

                terme = input("Recherche : ")
                res = tournoi.rechercher_equipe(terme)
                if not res:
                    print("Aucune équipe trouvée.")
                for e in res:
                    print(f"  [{e.id}] {e.nom} — {len(e.joueurs)} joueurs")
                print("Appuyez sur ENTER pour continuer")
                input()
                

            elif choix == "12":
                print("\033[H\033[J", end="")
                print("\n" + "=" * 55)
                print(f"{tournoi_name} - Historiques")
                print("=" * 55)

                print("\n--- HISTORIQUE ---")
                for h in tournoi.historique[-30:]:
                    print(f"  {h['date']} : {h['action']}")
                print("Appuyez sur ENTER pour continuer")
                input()


            elif choix == "0":
                print("MERCI D'AVOIR UTILISE MON APPLICATION VERSION CONSOLE!")
                sys.exit(0)

            else:
                print("❌ Choix invalide.")

        except ValueError as e:
            print(f"❌ Opération refusée : {e}")
        
            print("Appuyez sur ENTER pour continuer")
            input()



if __name__ == "__main__":
    main()