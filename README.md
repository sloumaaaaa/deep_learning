# 🎓 ESB Academic Assistant - Streamlit Edition

Une application de chatbot multilingue alimentée par RAG (Retrieval-Augmented Generation) pour l'Ecole Supérieure de Business (ESB).

## Caractéristiques

- 🌐 **Multilingual Support**: Anglais, Français, et Arabe
- 🤖 **RAG-powered**: Utilise la récupération de documents combinée avec un LLM
- 💬 **Chat Interface**: Interface de conversation intuitive avec Streamlit
- 🎯 **Context-aware**: Comprend l'historique de la conversation
- ⚡ **Fast & Efficient**: Mise en cache des composants pour les performances
- 🎨 **User-friendly**: Interface propre et responsive

## Installation

### Prérequis

- Python 3.8+
- pip

### Étapes d'installation

1. **Clonez ou téléchargez le projet**

```bash
cd c:\Users\[YourUsername]\Desktop\Rag
```

2. **Installez les dépendances**

```bash
pip install -r requirements.txt
```

3. **Configurez vos clés API**

Créez un fichier `.streamlit/secrets.toml` dans le répertoire du projet:

```toml
GROQ_API_KEY = "votre_clé_api_groq_ici"
GOOGLE_API_KEY = "votre_clé_api_google_ici"
```

Ou définissez les variables d'environnement:

```bash
set GROQ_API_KEY=votre_clé_api_groq_ici
set GOOGLE_API_KEY=votre_clé_api_google_ici
```

4. **Assurez-vous que le fichier de données existe**

Le fichier `data_esb.txt` doit être dans le même répertoire que `app.py`

## Utilisation

Pour lancer l'application:

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

## Comment utiliser le chatbot

1. **Sélectionnez votre langue**: English, Français, ou عربي
2. **Cliquez sur "Continue"** pour commencer la conversation
3. **Posez vos questions** sur les programmes d'étude de l'ESB
4. **Changez de langue** ou **effacez le chat** depuis la barre latérale
5. **Dites "bye", "au revoir" ou "وداعاً"** pour quitter

## Architecture

```
┌─────────────────────────────────────────┐
│     Streamlit Web Interface             │
├─────────────────────────────────────────┤
│     User Input & Session Management     │
├─────────────────────────────────────────┤
│     RAG Chain (Retrieval & Generation)  │
├─────────────────────────────────────────┤
│  Vector Store (Chroma) & Embeddings     │
├─────────────────────────────────────────┤
│    LLM (Llama 3.3 via Groq API)        │
└─────────────────────────────────────────┘
```

## Composants clés

- **LLM**: Llama 3.3 70B (via Groq API)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: Chroma
- **Framework Web**: Streamlit
- **Document Loader**: TextLoader (UTF-8)

## Fichiers du projet

```
Rag/
├── app.py                    # Application Streamlit
├── chatbot.ipynb             # Notebook Jupyter avec l'historique
├── data_esb.txt              # Données ESB
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

## Dépannage

### Erreur: "data_esb.txt not found"
- Assurez-vous que le fichier `data_esb.txt` est dans le même répertoire que `app.py`

### Erreur: "API key not found"
- Définissez la variable d'environnement `GROQ_API_KEY`
- Ou créez un fichier `.streamlit/secrets.toml` avec votre clé API

### Performances lentes
- La première exécution chargera tous les modèles - c'est normal
- Les exécutions suivantes seront plus rapides grâce à la mise en cache

## Contribuer

N'hésitez pas à améliorer ce projet et à soumettre des pull requests!

## Licence

Ce projet est fourni tel quel pour des fins éducatives.

## Support

Pour toute question ou problème, veuillez créer une issue dans le projet.

---

**Créé avec ❤️ pour ESB** | **Powered by LangChain & Streamlit**
