### 1. Branch Handling
<p><strong>Main Branch</strong>: nur durch Merge Request von <strong>Dev</strong> auf Main möglich.<br>
  <strong>Dev Branch</strong>: Sichere Testumgebung, nur von <strong>Feature/XXX Branch</strong> Merge auf Dev möglich.<br>
  <strong>Feature/XXX</strong> Branch <strong>eigener Branch</strong> für Entwicklung und zum mergen auf Dev erforderlich.</p>


### 2. Links
https://cryptopals.com/


### 3. BE 
Service URI
    postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/defaultdb?sslmode=require
Database name
    SecureChat

Tables:
	"Users" ("" nicht vergessen)
Host
    pg-3ec1ff15-justinjd00-e424.e.aivencloud.com
Port
    16693
User
    avnadmin
Password
    AVNS_wwY6Tw8KwsNrL5cWf5Z

#### 3.1 Database Control mit PSQL
* öffne psql
* gebe alles ein
* dann kann man SQL Befehle ausführen


Dokumentation:
https://aiven.io/docs/products/postgresql/get-started