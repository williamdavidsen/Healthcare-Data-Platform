# Healthcare Data Platform

Bu proje benim uçtan uca bir healthcare data pipeline çalışmam.
Public sağlık datalarını alıyor, temizliyor, kontrol ediyor, PostgreSQL ve dbt ile modele çeviriyor.
Sonra bu datayı FastAPI ve React dashboard ile gösteriyor.

Amacım medical karar vermek değil. Bu proje tanı koymaz.
Ben burada daha çok gerçek bir data engineering iş akışını göstermek istedim.

## İşveren İçin Kısa Sonuç

Bu proje şunu gösteriyor:

- Ham data kaynaktan alınır.
- Data kalite kontrollerinden geçer.
- PostgreSQL'e yazılır.
- dbt ile staging ve mart tabloları hazırlanır.
- API bu mart datayı servis eder.
- Dashboard bu datayı okunabilir hale getirir.
- Testler, CI ve Docker ile proje tekrar çalıştırılabilir olur.

Gerçek işte bu proje şuna benziyor:

Bir health analytics ekibi farklı public kaynaklardan data alıyor.
Bu datayı tek bir güvenilir tabloya çeviriyor.
Ürün ekibi, dashboard ekibi veya analistler bu tabloyu API üstünden kullanıyor.

## Bu Projede Ne Öğrendim

Bu projede data pipeline'ın sadece kod yazmak olmadığını daha iyi gördüm.
Data almak kolay gibi duruyor, ama asıl iş data doğru mu, eksik mi, tekrar çalışır mı kısmı.

Öğrendiğim ana şeyler:

- Ingestion kodunu modüler tutmak.
- Data schema kontrolü yapmak.
- Test yazmadan pipeline'a güvenmemek.
- dbt ile raw data ve analytics data ayrımını yapmak.
- API ve dashboard tarafını aynı mart data üstüne bağlamak.
- Docker ve CI ile projeyi başka makinada da çalışır hale getirmek.

## Pipeline Adımları

```text
Public datasets
  OWID CSV + WHO/CDC connector
        |
        v
Python ingestion
        |
        v
Raw files + PostgreSQL raw schema
        |
        v
dbt staging models
        |
        v
dbt analytics mart
        |
        +--> FastAPI
        +--> React dashboard
        +--> Streamlit old dashboard
```

Architecture diagram source: [docs/architecture.mmd](docs/architecture.mmd)

Pipeline basit olarak böyle çalışıyor:

1. OWID healthcare datası indirilir.
2. Gerekli kolonlar kontrol edilir.
3. Data local dosyaya ve istersem PostgreSQL'e yazılır.
4. dbt staging modeli raw tabloyu temizler.
5. dbt mart modeli dashboard için hazır tablo üretir.
6. FastAPI summary, trend, quality ve insight endpointlerini verir.
7. React dashboard bu endpointlerden datayı okur.

## Data Quality Nasıl Test Ediliyor

Data kaliteyi birkaç yerde kontrol ettim.

- Python validation required kolonları kontrol eder.
- Dataset boş mu bakılır.
- `country` ve `year` boş mu bakılır.
- Numeric olması gereken kolonlar numeric mi bakılır.
- pytest ingestion, analytics ve API davranışlarını test eder.
- dbt tarafında model parse ve dbt test CI içinde çalışır.
- API'de `/quality` ve `/freshness` endpointleri data durumunu gösterir.

Bu yüzden sadece dashboard yapmakla kalmadım.
Data bozulursa testlerin bunu yakalamasını istedim.

## Tech Stack

- Python: ingestion, validation, analytics
- PostgreSQL: raw ve modeled data storage
- dbt: staging ve mart modelleri
- FastAPI: analytics API
- React + Vite: main dashboard
- Streamlit: eski dashboard
- Docker Compose: local full-stack ortam
- pytest: otomatik testler
- GitHub Actions: CI ve scheduled pipeline check

## Nasıl Çalıştırılır

Önce dependency kur:

```bash
pip install -r requirements.txt
```

Windows için en kolay yol:

```powershell
.\start.ps1
```

Bu komut OWID datasını almaya çalışır.
API ve React frontend'i başlatır.
Eğer OWID tarafı o an çalışmazsa sample data ile devam eder.

Local adresler:

- React dashboard: http://127.0.0.1:5173
- FastAPI docs: http://127.0.0.1:8002/docs

PostgreSQL ile çalıştırmak için:

```powershell
.\start.ps1 -WithPostgres
```

OWID datasını PostgreSQL'e yazıp dbt modellerini de build etmek için:

```powershell
.\start.ps1 -WithPostgres -WriteDb
```

Bu modda API şu dbt mart tablosunu okur:

```text
analytics.mart_country_health_trends
```

Oluşan ana tablolar:

- `raw.health_indicators`
- `analytics.stg_health_indicators`
- `analytics.mart_country_health_trends`

## Faydalı Komutlar

Sadece pipeline:

```powershell
.\scripts\run_pipeline.ps1
```

dbt çalıştır:

```powershell
.\scripts\run_dbt.ps1
```

Local kontroller:

```powershell
.\scripts\check_project.ps1
```

Docker full stack:

```powershell
.\scripts\start_docker.ps1
```

Docker Compose ile manuel:

```bash
docker compose up -d postgres
docker compose --profile pipeline run --rm pipeline
docker compose up -d api frontend
```

Python orchestration entrypoint:

```bash
python -m src.orchestration.pipeline
```

WHO metadata indir:

```bash
python -m src.ingestion.load_who --limit 100
```

CDC catalog metadata indir:

```bash
python -m src.ingestion.load_cdc --limit 100
```

Sample data kullan:

```powershell
.\start.ps1 -UseSample
```

Eski Streamlit dashboard:

```powershell
.\start.ps1 -UseStreamlit
```

Testleri çalıştır:

```bash
pytest
```

Frontend build:

```bash
npm run build --prefix frontend
```

API çalıştır:

```bash
uvicorn api.main:app --reload
```

React frontend çalıştır:

```bash
cd frontend
npm install
npm run dev
```

PostgreSQL backup al:

```powershell
.\scripts\backup_postgres.ps1
```

Backup restore et:

```powershell
.\scripts\restore_postgres.ps1 -BackupPath .\backups\healthcare-YYYYMMDD_HHMMSS.dump
```

## API Endpointleri

Örnek endpointler:

- `GET /summary?limit=100&offset=0&sort_by=life_expectancy&sort_dir=desc`
- `GET /indicators?country=Norway&metric=life_expectancy`
- `GET /trend?country=Norway`
- `GET /freshness`
- `GET /quality`
- `GET /correlations`
- `GET /insights`
- `GET /anomalies?metric=health_risk_score`

## Data Sources

- Our World in Data: life expectancy, diabetes prevalence, obesity, health spending, GDP
- World Health Organization Global Health Observatory metadata connector
- Centers for Disease Control and Prevention catalog / Socrata connector

## Projede Olanlar

- OWID ingestion
- WHO ve CDC connector entrypointleri
- PostgreSQL raw table
- dbt staging ve mart modelleri
- FastAPI analytics API
- React dashboard
- Streamlit legacy dashboard
- Correlation analysis
- Risk index
- Year-over-year değişimler
- Anomaly detection
- Freshness ve quality endpointleri
- Pagination ve filtering
- Backup / restore scriptleri
- Docker Compose
- GitHub Actions CI
- Scheduled pipeline workflow

## Screenshot

![Healthcare Data Platform dashboard](docs/screenshots/dashboard.png)

Screenshot almak için:

```powershell
.\scripts\capture_screenshots.ps1
```

## Şu Anki Durum

Proje şu an çalışır durumda.
Python testleri, ruff kontrolü, frontend build ve dbt parse kontrolünden geçti.

Phase 2 ve Phase 3 tamam.
Phase 4 advanced özellikleri de eklendi.

Pipeline OWID datasını alabilir.
PostgreSQL'e yazabilir.
dbt staging ve mart modellerini çalıştırabilir.
FastAPI bu mart datayı React dashboard'a servis eder.

Not: Dataset annual datadır, daily data değildir.
Current year için kaynakta yayınlanan en yakın değerler kullanılır.

## Medical Disclaimer

Bu proje sadece eğitim ve portfolio amaçlıdır.
Medical advice, diagnosis veya treatment recommendation vermez.
