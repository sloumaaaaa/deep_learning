# COMMANDES À EXÉCUTER POUR LANCER VOTRE PROJET RAG

## 🎯 SOLUTION RAPIDE (Copier-Coller)

Ouvrez PowerShell et exécutez EXACTEMENT ces commandes dans cet ordre:

```powershell
cd "C:\Users\msamet\Desktop\Rag"
pip install --upgrade pip
pip install streamlit langchain langchain-community langchain-core langchain-groq langchain-chroma sentence-transformers chromadb langchain-text-splitters
streamlit run app.py
```

Voilà! L'app s'ouvrira automatiquement dans votre navigateur! 🚀

---

## 📋 DÉTAIL LIGNE PAR LIGNE

### Ligne 1: Allez dans le dossier du projet
```powershell
cd "C:\Users\msamet\Desktop\Rag"
```
👉 Cela change le répertoire actuel vers votre projet

### Ligne 2: Mettez à jour pip
```powershell
pip install --upgrade pip
```
👉 Cela met à jour l'outil d'installation de packages

### Ligne 3: Installez les dépendances
```powershell
pip install streamlit langchain langchain-community langchain-core langchain-groq langchain-chroma sentence-transformers chromadb langchain-text-splitters
```
👉 Cela installe TOUS les packages nécessaires pour votre projet RAG
⏱️ Cela peut prendre 2-5 minutes

### Ligne 4: Lancez l'application
```powershell
streamlit run app.py
```
👉 Cela démarre votre application Streamlit
✅ L'app s'ouvrira automatiquement à http://localhost:8501

---

## 🔄 LES FOIS SUIVANTES

Après la première installation, vous n'avez besoin que de:

```powershell
cd "C:\Users\msamet\Desktop\Rag"
streamlit run app.py
```

---

## ⚡ ALTERNATIVES RAPIDES

### Option 1: Double-cliquez sur launch.bat
Le fichier `launch.bat` exécute tout automatiquement!
- Cherchez le fichier `launch.bat` dans le dossier Rag
- Double-cliquez dessus
- Attendez que tout s'installe et se lance

### Option 2: Double-cliquez sur setup.ps1
Le fichier `setup.ps1` est un script PowerShell
- Cherchez le fichier `setup.ps1` dans le dossier Rag
- Double-cliquez dessus
- Attendez

### Option 3: Utilisez run.py
```powershell
cd "C:\Users\msamet\Desktop\Rag"
python run.py
```

---

## ❓ QUESTIONS FRÉQUENTES

**Q: Que faire si j'obtiens une erreur?**
A: Vérifiez que vous avez bien exécuté toutes les 4 commandes dans l'ordre

**Q: L'app est lente au démarrage?**
A: Normal! Le chargement des modèles prend 1-2 minutes la première fois

**Q: Comment arrêter l'application?**
A: Appuyez sur `Ctrl + C` dans PowerShell

**Q: Peut-je utiliser une autre langue?**
A: Oui! L'app supporte l'anglais, le français et l'arabe

**Q: Où trouver le fichier data_esb.txt?**
A: Il doit être dans C:\Users\msamet\Desktop\Rag\

---

**C'est tout! Vous êtes prêt à démarrer!** 🎉
