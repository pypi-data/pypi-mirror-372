<p align="center">
  <img src="banner.png" alt="CVVCalendarSync Banner" width="800">
</p>

# CVVCalendarSync

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-343-blue.svg)]()
[![PyPI](https://img.shields.io/pypi/v/cvvcalendarsync)](https://pypi.org/project/cvvcalendarsync/)
[![CI Tests](https://github.com/LNLenost/CVVCalendarSync/actions/workflows/ci.yml/badge.svg)](https://github.com/LNLenost/CVVCalendarSync/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/LNLenost/CVVCalendarSync/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/LNLenost/CVVCalendarSync/actions/workflows/publish-pypi.yml)

Un script Python per sincronizzare automaticamente gli eventi del registro elettronico Classeviva con Google Calendar.

## 🔗 Progetto Originale

Questo progetto è un fork migliorato del repository originale:
- **Repository**: [LucaCraft89/CVVCalendarSync](https://github.com/LucaCraft89/CVVCalendarSync)
- **Autore**: LucaCraft89
- **Licenza**: GPL-3.0

## 📊 Statistiche del Progetto

- **Linguaggi Principali**: Python
- **Linee di Codice**: 343
- **Dipendenze**: 4 (requests, google-auth, google-api-python-client, google-auth-oauthlib)
- **Compatibilità**: Linux, macOS, Windows
- **Disponibile su PyPI**: ✅

## ✨ Caratteristiche

- 🔄 **Sincronizzazione Automatica**: Aggiorna il calendario Google con gli eventi di Classeviva
- 🗑️ **Gestione Eventi Duplicati**: Rimuove automaticamente eventi duplicati o eliminati
- ⏰ **Esecuzione Programmata**: Supporta esecuzione automatica ogni 20 minuti via cron
- 🛡️ **Gestione Errori**: Gestisce errori API e stati temporanei (es. anno scolastico non iniziato)

## 📋 Prerequisiti

- Python 3.8+
- Account Google con Calendar API abilitata
- Credenziali Classeviva valide
- File di configurazione `config.json` e `credentials.json`

## 🚀 Installazione

### Opzione 1: Installazione da PyPI (Consigliata)

1. **Installa il pacchetto:**
   ```bash
   pip install cvvcalendarsync
   ```

2. **Esegui lo script:**
   ```bash
   cvvcalendarsync
   ```

### Opzione 2: Installazione da Sorgente

1. **Clona il repository:**
   ```bash
   git clone https://github.com/LNLenost/CVVCalendarSync.git
   cd CVVCalendarSync
   ```

2. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Esegui lo script:**
   ```bash
   python classevivaSync.py
   # oppure
   python -m cvvcalendarsync
   ```

## ⚙️ Configurazione

**⚠️ IMPORTANTE**: Prima di eseguire lo script, devi configurare i file richiesti nella directory di lavoro!

### 1. Crea il file config.json
Crea un file `config.json` nella directory dove eseguirai lo script:

```json
{
  "user_id": "tuo_user_id_classeviva",
  "user_pass": "tua_password_classeviva",
  "calendar_id": "tuo_calendar_id_google@group.calendar.google.com",
  "credentials_file": "credentials.json"
}
```

### 2. Scarica credentials.json
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita l'API Google Calendar
4. Crea credenziali (Service Account Key) e scarica `credentials.json`
5. Salva il file nella stessa directory di `config.json`

## 📖 Utilizzo

### Esecuzione Manuale

**Con PyPI:**
```bash
cvvcalendarsync
```

**Da sorgente:**
```bash
python classevivaSync.py
# oppure
python -m cvvcalendarsync
```

### Esecuzione Automatica (ogni 20 minuti)

**Con PyPI:**
```bash
crontab -e
```
Aggiungi questa riga:
```
*/20 * * * * cvvcalendarsync
```

**Da sorgente:**
```bash
crontab -e
```
Aggiungi questa riga:
```
*/20 * * * * /usr/bin/python3 /percorso/completo/al/progetto/classevivaSync.py
```

### Output di Esempio
```
Effettuato il login con il profilo NOME COGNOME
{
    "periods": [
        {
            "dateStart": "2025-09-01",
            "dateEnd": "2025-12-31",
            ...
        }
    ]
}
Aggiungo evento: Lezione di Matematica - 2025-09-01T08:00:00+02:00 to 2025-09-01T09:00:00+02:00
```

## 🛠️ Gestione Errori

### Anno Scolastico Non Iniziato
Se l'anno scolastico non è ancora attivo, lo script mostrerà:
```
[INFO] L'anno scolastico non è ancora iniziato. Riprova quando sarà attivo nel registro elettronico.
```

### Errori di Autenticazione
- Verifica che `user_id` e `user_pass` siano corretti
- Assicurati che `credentials.json` sia valido e con permessi adeguati

### Errori API
- Controlla la connessione internet
- Verifica che l'account Classeviva sia attivo

## 📁 Struttura del Progetto

```
CVVCalendarSync/
├── classevivaSync.py    # Script principale
├── config.json          # Configurazione (non tracciato)
├── credentials.json     # Credenziali Google (non tracciato)
├── requirements.txt     # Dipendenze Python
├── Dockerfile           # Container Docker
├── compose.yml          # Docker Compose
├── LICENSE              # Licenza GPL-3.0
├── README.md            # Questa documentazione
└── .gitignore           # File da ignorare in git
```

## 🐳 Docker (Opzionale)

### Build e Run
```bash
docker build -t cvvcalendarsync .
docker run -v $(pwd)/config.json:/app/config.json -v $(pwd)/credentials.json:/app/credentials.json cvvcalendarsync
```

### Docker Compose
```bash
docker-compose up
```

## 🤝 Contributi

Contributi benvenuti! Per favore:

1. Fork il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le tue modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è distribuito sotto **GNU General Public License 3.0 (GPL-3.0)**.
Vedi il file `LICENSE` per i termini completi della licenza.

## ⚠️ Disclaimer

Questo progetto non è ufficialmente affiliato con Classeviva o Google. Utilizzalo a tuo rischio. Assicurati di rispettare i termini di servizio di entrambi i servizi.

## 📞 Supporto

Se hai problemi:
1. Controlla i log di output dello script
2. Verifica la configurazione (config.json e credentials.json)
3. Assicurati di aver seguito tutte le istruzioni di configurazione
4. Apri una issue su GitHub con il messaggio di errore completo

## 📦 Utilizzo come Libreria Python

Dopo aver installato il pacchetto da PyPI, puoi anche usarlo come libreria:

```python
from cvvcalendarsync import login, get_agenda, sync_to_google_calendar

# Effettua il login
login_response = login("tuo_user_id", "tua_password")

# Ottieni l'agenda
agenda = get_agenda("11920234", "20250901", "20251231", login_response["token"])

# Sincronizza con Google Calendar
sync_to_google_calendar(agenda, "calendar_id@group.calendar.google.com", "credentials.json")
```

## 🚀 Pubblicazione su PyPI

Per pubblicare nuove versioni su PyPI:

```bash
# Installa gli strumenti di build
pip install --upgrade build twine

# Costruisci il pacchetto
python -m build

# Pubblica su PyPI (richiede account)
twine upload dist/*
```

---

⭐ Se questo progetto ti è utile, considera di mettere una stella!
