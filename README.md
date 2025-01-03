# Datenbeziehung aus TTN
Im Root-Verzeichnis des Repositories befindet sich ein Skript, das die Daten von TTN mittels MQTT herunterlädt und in die Datenbank speichert.
Für manuelle Warnungen und Tests existiert außerdem die Datei `fcm.py`.

# API für die App und Website
Unter `warnMeApi/express-api` befindet sich die API, die die App mit den Wasserstandsdaten versorgt. Zudem empfängt die API die MQTT-Konfigurationsdaten der Sensoren anderer Nutzer von der Website und speichert diese in der Datenbank.

# Weiterführende Links
- Repository für die App: [WarnMe-App](https://github.com/NiklasHubGit/WarnMe-App)
- Unsere Homepage mit Bauanleitung und weiteren Informationen: [WarnMe](https://warnme.info/)

