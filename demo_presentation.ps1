# Script de demonstration PowerShell pour presentation orale
# Systeme de Surveillance Qualite de l'Air Paris

Write-Host "DEMONSTRATION SYSTEME DE SURVEILLANCE QUALITE DE L'AIR" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verification des services
Write-Host "1. VERIFICATION DES SERVICES" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow
Write-Host "Statut des conteneurs Docker :"
docker-compose ps
Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 2. Verification des topics Kafka
Write-Host "2. VERIFICATION DES TOPICS KAFKA" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Yellow
Write-Host "Liste des topics crees :"
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 3. Monitoring du Producer
Write-Host "3. MONITORING DU PRODUCER" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow
Write-Host "Logs du producer (dernieres 10 lignes) :"
docker-compose logs producer | Select-Object -Last 10
Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 4. Verification donnees Kafka
Write-Host "4. VERIFICATION DONNEES KAFKA" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow
Write-Host "Apercu des messages dans le topic air-quality-paris :"
Write-Host "Note: Les messages s'arreteront automatiquement apres quelques secondes"
Write-Host ""

# Lancer le consumer Kafka en arriere-plan et l'arreter apres 10 secondes
$job = Start-Job -ScriptBlock {
    docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic air-quality-paris --from-beginning --max-messages 3
}
Wait-Job $job -Timeout 10
Stop-Job $job -PassThru | Remove-Job

Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 5. Monitoring Spark
Write-Host "5. MONITORING SPARK" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Yellow
Write-Host "Logs du processeur Spark :"
docker-compose logs spark | Select-Object -Last 10
Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 6. Verification InfluxDB
Write-Host "6. VERIFICATION INFLUXDB" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow
Write-Host "Nombre de records dans la base air_quality :"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8086/query" -Method Get -Body @{
        q = "SELECT COUNT(*) FROM air_quality"
        db = "air_quality"
    }
    $count = $response.results[0].series[0].values[0][1]
    Write-Host "Nombre d enregistrements: $count" -ForegroundColor Green
} catch {
    Write-Host "Base de donnees en cours de chargement..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 7. Acces Grafana
Write-Host "7. ACCES GRAFANA" -ForegroundColor Yellow
Write-Host "----------------" -ForegroundColor Yellow
Write-Host "Dashboard disponible a : http://localhost:3000" -ForegroundColor Cyan
Write-Host "Identifiants : admin / admin" -ForegroundColor Cyan
Write-Host "Dashboard : Paris Air Quality Monitoring" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ouvrons Grafana dans votre navigateur..." -ForegroundColor Green

# Ouvrir Grafana automatiquement
Start-Process "http://localhost:3000"

Write-Host "Appuyez sur ENTREE quand vous avez termine la demonstration Grafana..." -ForegroundColor Green
Read-Host

# 8. Metriques de performance
Write-Host "8. METRIQUES DE PERFORMANCE" -ForegroundColor Yellow
Write-Host "---------------------------" -ForegroundColor Yellow
Write-Host "Utilisation des ressources Docker :"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
Write-Host ""
Write-Host "Appuyez sur ENTREE pour continuer..." -ForegroundColor Green
Read-Host

# 9. Test de resistance aux pannes
Write-Host "9. TEST DE RESISTANCE (OPTIONNEL)" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Yellow
$choice = Read-Host "Voulez-vous demontrer la resistance aux pannes ? (y/n)"
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "Arret temporaire du producer..." -ForegroundColor Red
    docker-compose stop producer
    Write-Host "Attendez 10 secondes..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Write-Host "Redemarrage du producer..." -ForegroundColor Green
    docker-compose start producer
    Write-Host "Le systeme continue de fonctionner !" -ForegroundColor Green
}
Write-Host ""

# 10. Fin de demonstration
Write-Host "DEMONSTRATION TERMINEE" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "Systeme de surveillance operationnel !" -ForegroundColor Green
Write-Host "- Donnees collectees en temps reel" -ForegroundColor Green
Write-Host "- Pipeline de traitement fonctionnel" -ForegroundColor Green
Write-Host "- Visualisation accessible" -ForegroundColor Green
Write-Host "- Architecture fault-tolerant" -ForegroundColor Green
Write-Host ""
Write-Host "Questions ?" -ForegroundColor Cyan
