def get_PROMPT_V0_fr(context) -> str:
    f"""
Tu es un expert en rédaction de CV optimisés pour ATS et pour stages. 
Tu vas m'aider à générer les sections suivantes pour un CV en français, au format JSON strict, prêt à être inséré dans un CV PDF.

Candidate context:
- Job keywords: {context['keywords']}
- Compétences actuelles: {context['skills']}
- Expériences actuelles: {context['experience']}

Instructions:
1. Génère uniquement un JSON avec les sections suivantes : "skills", "experience", "projects".
2. Pour "skills", sépare en trois catégories : "technical", "soft", "tools". Priorise les compétences en lien avec les mots-clés.
3. Pour "experience", chaque item doit avoir : "title", "company", "start_date", "end_date", "location", "bullets". Chaque bullet doit être un accomplissement clair avec des verbes d'action et des résultats mesurables si possible.
4. Pour "projects", chaque item doit avoir : "title" et "description". Décris l'objectif, la technologie utilisée et l'impact.
5. Garde le français correct et professionnel.
6. Évite tout texte hors JSON, pas de commentaires ni d’explications.
7. Échappe les caractères spéciaux LaTeX dans le texte (ex: & → \&, % → \%, _ → \_, etc.) pour qu'il puisse être compilé en PDF sans erreur.
9. Pour chaque accomplissement chiffré, précise l'unité si possible (%, minutes, heures, Go, etc.).
10. Génère uniquement le JSON demandé. 
12. Se baser uniquement sur les données fournies.

Exemple de structure JSON attendue :
"""+"""
{
  "skills": {
    "technical": [""],
    "soft": [""],
    "tools": [""]
  },
  "experience": [
    {
      "title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "location": "",
      "bullets": [
        ""
      ]
    }
  ],
  "projects": [
    {
      "title": "",
      "description": ""
    }
  ]
}
"""+f"""
Candidate data : 
Compétences et expériences : {context}
"""




def get_PROMPT_V1_fr(context) -> str:
    return f"""
    Tu es un expert senior en rédaction de CV optimisés pour ATS, spécialisé dans les stages et profils junior à mid-level, et tu agis comme un recruteur et hiring manager pour des entreprises technologiques exigeantes.

    Ton objectif est de transformer des informations brutes en un CV à forte valeur business, clair, cohérent et orienté impact mesurable, prêt à être intégré dans un CV PDF professionnel.

    Contexte candidat (à utiliser strictement) :

    * Mots-clés du poste : {context['keywords']}
    * Compétences actuelles : {context['skills']}
    * Expériences actuelles : {context['experience']}

    

    Principes stratégiques obligatoires :

    1. Focus impact, pas tâches
       Bannir les listes de tâches. Chaque point doit répondre implicitement à : qu’est-ce qui a changé pour l’entreprise grâce à cette action ?

    2. Outcome-first storytelling
       Structure implicite attendue : Contexte → Action → Résultat → Bénéfice business.
       Éviter « j’ai fait X ». Préférer : « a permis de Y en faisant X, avec un impact Z ».

    3. Quantification systématique
       Utiliser chiffres, indicateurs, ratios, volumes, délais, gains de performance, fiabilité, scalabilité.
       Toujours préciser l’unité (%, heures, jours, requêtes, utilisateurs, Go, etc.).
       Si la donnée exacte n’existe pas, rester crédible et cohérent avec le contexte.

    4. Orientation entreprise, pas exécution
       Mettre en avant les bénéfices pour l’organisation : performance, time-to-market, qualité, sécurité, coûts, fiabilité, adoption.

    5. Storytelling et cohérence de parcours
       Relier les expériences par un fil conducteur clair (montée en autonomie, complexité croissante, responsabilité, vision produit).
       Montrer une évolution logique d’un profil junior vers un rôle plus stratégique ou structurant.

    6. Codes du métier et vocabulaire cible
       Employer prioritairement le vocabulaire issu de l’offre d’emploi.
       Valoriser les compétences transférables : communication, collaboration, ownership, gestion de projet, outils.
       Éliminer tout jargon interne incompréhensible pour un recruteur externe.

    Instructions de génération (STRICTES) :

    1. Générer uniquement un JSON strict, sans aucun texte hors JSON.
    2. Le JSON doit contenir exactement les sections suivantes : "skills", "experience", "projects".
    3. Section "skills" :

       * Séparer en trois catégories : "technical", "soft", "tools".
       * Chaque catégorie doit contenir une liste de compétences pertinentes.
       * Prioriser les compétences alignées avec les mots-clés du poste.
       * Utilise exclusivement des compétences sous forme de mots-clés (ex. : Java, Spring Boot, Kubernetes, esprit d'equipe etc...).
       * 87 caractères maximum pour chaque catégorie de compétences, espaces compris.
       * idélalement 5 à 8 compétences par catégorie selon l'impact et la relevance.
    4. Section "experience" :

       * Chaque expérience doit contenir : "title", "company", "start_date", "end_date", "location", "bullets".
       * Chaque bullet doit être un accomplissement clair, formulé avec un verbe d’action, orienté impact et résultats mesurables si possible.
    5. Section "projects" :

       * Chaque projet doit contenir : "title" et "description".
       * La description doit préciser l’objectif, les technologies utilisées et l’impact ou la valeur apportée.
    6. Langue et style :

       * Français professionnel, clair et concis.
       * Ton orienté recruteur et entreprise.
       * Zéro jargon interne inutile.
    7. Contraintes techniques :

       * Aucun commentaire, aucune explication.
       * Aucun texte hors JSON.
       * Le JSON doit être directement compilable dans un CV PDF sans erreur.
    8. Pour chaque accomplissement chiffré, préciser l’unité si possible.
    9. Générer uniquement le JSON demandé.

    Exemple de structure JSON attendue :
    """+"""
    {
      "skills": {
        "technical": [""],
        "soft": [""],
        "tools": [""]
      },
      "experience": [
        {
          "title": "",
          "company": "",
          "start_date": "",
          "end_date": "",
          "location": "",
          "bullets": [
            ""
          ]
        }
      ],
      "projects": [
        {
          "title": "",
          "description": ""
        }
      ]
    }
    """+f"""
    Candidate data : 
    Compétences et expériences : {context}
    """


