import os
from groq import Groq

client = Groq(api_key="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")

def generate_cv_section(context):
    prompt = f"""
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



    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0.2,
        max_tokens=50000  
    )
    print(f"llm response: {response}")

    return response.choices[0].message.content

