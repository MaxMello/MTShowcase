# MT Showcase
![Home Page](http://i.imgur.com/RKzy6JS.png)
## Funktionsbeschreibung
Der MT Showcase ist eine Ausstellungsplattform für Studierendenprojekte des Departments Medientechnik der HAW Hamburg.
Er bietet folgenden Funktionsumfang:
* Dynamische Homepage mit Tag-Filterung, Suchfunktion und Sortierfunktion
* Registrierung als Student oder Professor / Betreuer
* Anlegen eines Nutzerprofils inklusive Profilbild und Verbindungen zu Netzwerken (z.B. Github, XING, Facebook)
    * Alle eigenen Projekte werden automatisch verlinkt
* Projekte, die im Rahmen der Hochschule entstanden sind, über ein Upload-Interface hochladen
    * Verlinkung von Teammitgliedern und Betreuern
    * Angabe von Metadaten und Tags
    * Angabe von grundlegenden Daten (Titel, Untertitel, Kurzbeschreibung)
    * Variable Menge an Medien (Bilder, Videos, Audio, Texte, Slideshows) mit File-Upload und Embedded Playern (YouTube, Vimeo, Soundcloud)
        * Individuelle Sichtbarkeitseinstellungen pro Medien-Inhalt
    * Verlinkung von weiteren Ressourcen (z.B. Webseite, Github-Repository)
* Professoren-Interface zur Freigabe von Projekten inkl. automatisierter E-Mails
* Übersicht über meine bearbeitbaren Projekte
* Nutzer- und Privatsphäre-Einstellungen
    * Globale Anonymisierung mit Usernamen statt Klarnamen möglich
    * Projektspezifisch bestimmen, ob man angezeigt werden möchte
## Ziele und Vision
Der MT Showcase soll als Anlaufstelle für Studierende, Professoren und Studieninteressierte eine Schnittstelle bilden, über welche die 
gesammelten Studierendenprojekte des Departments Medientechnik sichtbar und langlebig platziert werden.
## Technologien
Der MT Showcase ist mit dem Web-Framework Django in der Programmiersprache Python 3 geschrieben. Zusätzlich gibt es HTML5-Komponenten, sowie
 Javascript (+ jQuery) Code. Für das Styling der Webseite wurde mit dem CSS-Pre-Processor Less auf Bootstrap 3 mit einem Custom Theme aufgesetzt. Da Django mit einem ORM arbeitet, ist das DBMS grundsätzlich austauschbar,
 der MT Showcase ist allerdings in der Praxis mit MySQL umgesetzt.
## Projektstruktur
* ``MTShowcase/`` - Der Top-Level-Order für das Projekt, ohne eigentlichen Logik-Code
    * ``settings.py `` - Zentrale Datei für Einstellungen (z.B. Datenbank, Middlewares)
    * ``urls.py`` - Top Level File, in der alle URL-Definitionen inkludiert werden
* ``apps/`` - Unter dem apps-Ordner sind alle nach Funktionen getrennten Module (bei Django "Apps") vorhanden
    * ``home/`` - Funktionen für die Homepage der Seite, u.a. die Suchfunktion und Tags
    * ``user/`` - Nutzermodels, Profilseite und Nutzereinstellungen
    * ``project/`` - Projekt-Detailansicht und Projekt-Upload
    * ``authentication/`` - Registierung und Anmeldung
    * ``administration/`` - Admin & Professoren-Interface
* ``static/`` - Top Level Folder für statische Dateien, die von diversen Apps genutzt werden (Bilder, Styles, JS Libraries)
* ``templates/`` - Top Level Django-Templates, die in diversen Apps genutzt werden
* ``manage.py`` - Top-Level Python Script zum ausführen von Command Line Utilities von Django
* ``requirements.txt`` - Alle benötigten Dependencies, einfach über pip install -r requirements.txt innerhalb der VirtualEnv zu installieren
## Ansprechpartner
Der MT Showcase wird von Dirk Löwenstrom (@d1rkHH) und Max Wiechmann (@MaxMello) betreut und aktiv entwickelt.