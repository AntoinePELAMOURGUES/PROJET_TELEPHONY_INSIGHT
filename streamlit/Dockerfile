# Utiliser l'image de base Python 3.12
FROM python:3.12

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY ./requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copier les fichiers de l'application dans le conteneur
COPY ./app /app

# Définir le point d'entrée pour exécuter Streamlit
ENTRYPOINT ["streamlit", "run"]

# Spécifier le script à exécuter
CMD ["app.py"]