# 🔧 COMMANDES EXACTES POUR LA DÉMONSTRATION

## 🚀 SÉQUENCE DE DÉMARRAGE

```powershell
# 1. Aller dans le répertoire du projet
cd "c:\Users\Max\Documents\EFREI\Project-1"

# 2. Démarrer tous les services
docker-compose up -d

# 3. Attendre que tous les services soient prêts (2-3 minutes)
# Vous pouvez surveiller avec :
docker-compose logs -f producer
```

## 📋 COMMANDES DE DÉMONSTRATION

### **1. Vérifier le statut des services**
```powershell
docker-compose ps
```
**Résultat attendu :** Tous les services "Up"

### **2. Lister les topics Kafka créés**
```powershell
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```
**Résultat attendu :**
```
air-quality-paris
no2-topic
o3-topic
pm10-topic
pm25-topic
```

### **3. Voir les logs du producer en temps réel**
```powershell
docker-compose logs -f producer | Select-Object -Last 5
```
**Résultat attendu :** Messages toutes les 60 secondes avec "Sent real air quality data"

### **4. Voir un échantillon des messages Kafka**
```powershell
# Attention : Cette commande va tourner indéfiniment, utilisez Ctrl+C pour arrêter
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic air-quality-paris --from-beginning --max-messages 1
```

### **5. Vérifier les données dans InfluxDB**
```powershell
# Compter les enregistrements
Invoke-RestMethod -Uri "http://localhost:8086/query" -Method Get -Body @{q="SELECT COUNT(*) FROM air_quality"; db="air_quality"}

# Voir les derniers enregistrements
Invoke-RestMethod -Uri "http://localhost:8086/query" -Method Get -Body @{q="SELECT * FROM air_quality ORDER BY time DESC LIMIT 3"; db="air_quality"}
```

### **6. Ouvrir Grafana**
```powershell
# Ouvrir automatiquement dans le navigateur
Start-Process "http://localhost:3000"
```
**Login :** admin / admin  
**Dashboard :** Paris Air Quality Monitoring

### **7. Voir les logs Spark**
```powershell
docker-compose logs spark | Select-Object -Last 5
```

### **8. Statistiques des ressources**
```powershell
docker stats --no-stream
```

## 🎯 DONNÉES À MENTIONNER PENDANT LA DÉMO

### **Format des données JSON :**
```json
{
  "timestamp": "2025-07-01T14:30:00.000Z",
  "location": "Paris",
  "coordinates": {"lat": 48.8566, "lon": 2.3522},
  "aqi": 2,
  "components": {
    "co": 233.4,
    "no": 0.12,
    "no2": 19.3,
    "o3": 89.2,
    "so2": 8.1,
    "pm2_5": 12.5,
    "pm10": 18.7,
    "nh3": 2.1
  }
}
```

### **Métriques à mentionner :**
- **Fréquence de collecte :** 60 secondes
- **Nombre de polluants :** 8 (PM2.5, PM10, NO2, O3, CO, SO2, NH3, AQI)
- **Latence end-to-end :** < 5 secondes
- **Topics Kafka :** 5 avec 3 partitions chacun
- **Base de données :** InfluxDB (time-series)

## 🛠️ COMMANDES DE DÉPANNAGE

### **Si un service ne démarre pas :**
```powershell
# Redémarrer tout
docker-compose down
docker-compose up -d

# Vérifier les logs d'erreur
docker-compose logs [service_name]
```

### **Si Kafka ne répond pas :**
```powershell
# Vérifier que Kafka est prêt
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### **Si InfluxDB est vide :**
```powershell
# Créer la base manuellement
Invoke-RestMethod -Uri "http://localhost:8086/query" -Method Post -Body "q=CREATE DATABASE air_quality"
```

### **Si Grafana ne charge pas :**
```powershell
# Redémarrer Grafana uniquement
docker-compose restart grafana
```

## 📊 URLS IMPORTANTES

- **Grafana Dashboard :** http://localhost:3000
- **InfluxDB Admin :** http://localhost:8086
- **Spark UI :** http://localhost:4040 (si disponible)

## 🎤 SCRIPT DE PRÉSENTATION DES COMMANDES

### **Présenter la commande avant de l'exécuter :**

```
"Maintenant, vérifions que tous nos services sont opérationnels..."
→ docker-compose ps

"Comme vous pouvez le voir, nous avons 6 services qui tournent. Vérifions maintenant que Kafka a bien créé nos topics..."
→ docker-compose exec kafka kafka-topics --list

"Parfait ! Nos 5 topics sont créés. Regardons maintenant notre producer qui collecte les données en temps réel..."
→ docker-compose logs -f producer | Select-Object -Last 5

"Excellent ! Toutes les 60 secondes, notre producer récupère les données d'OpenWeatherMap. Jetons un œil aux données qui transitent dans Kafka..."
→ (montrer un message Kafka)

"Ces données sont ensuite traitées par Spark et stockées dans InfluxDB. Vérifions le nombre d'enregistrements..."
→ (commande InfluxDB)

"Et maintenant, le plus important : la visualisation dans Grafana !"
→ Start-Process "http://localhost:3000"
```

## 🔍 POINTS D'ATTENTION DURANT LA DÉMO

### **À surveiller :**
- [ ] Tous les services montrent "Up" dans docker-compose ps
- [ ] Les logs du producer montrent des succès récents
- [ ] Grafana affiche des données (pas de "No data")
- [ ] Les graphiques montrent une évolution temporelle

### **Si problème visible :**
- Rester calme et expliquer ce qui devrait se passer
- Utiliser les screenshots de sauvegarde
- Dire : "En production, nous aurions des alertes pour ce type de situation"

## 💡 ASTUCES PRÉSENTATION

### **Gérer les temps de chargement :**
```
"Pendant que cette commande s'exécute, laissez-moi vous expliquer..."
"Vous voyez ici que le système traite les données en temps réel..."
"Cette légère latence est normale et acceptable pour notre use case..."
```

### **Transitions fluides :**
```
"Maintenant que nous avons vu l'ingestion, passons au traitement..."
"Cette architecture nous permet de..."
"L'étape suivante de notre pipeline est..."
```

## 🎯 OBJECTIF DE CHAQUE COMMANDE

1. **docker-compose ps** → Prouver que le système fonctionne
2. **kafka topics list** → Montrer l'architecture de streaming
3. **producer logs** → Démontrer la collecte temps réel
4. **kafka consumer** → Visualiser les données qui transitent
5. **influxdb query** → Confirmer le stockage des données
6. **grafana** → Impact visuel final impressionnant

**Chaque commande raconte une partie de l'histoire de votre pipeline !**

---

**Vous êtes prêt ! 🚀 Confiance et passion = Succès garanti ! 💪**
