Skript zum converten der "EIN..." Datein von gkcanlag. Die main.py Datei kovertiert die "Ein.DBF" Datein aus dem "input" Ordner in verschiedene Datein.

Die gesamte Pipeline sieht wie folgt aus:

1. "EIN.DBF" Datein in den "input" Ordner legen
2. "main.py" ausführen
3. In Ordner "coverted_output": eine csv Version der "EIN.DBF" Datei
4. In Ordner "filtered_output": eine gefilterte Version der ein.csv, mit relevanten und umbenannten spalten 
5. temp: dieser Ordner sollte leer bleiben
6. In Ordner: "wirtschaftsjahre": Hier sind die Einträge der output_csv Datein nach Wirtschaftsjahren (01.07. - 30.06) sortiert

Um die Pipeline auszuführen müssen nur die "EIN.DBF" Datein in den "input" Ordner gelegt werden und "main.py" ausgeführt werden. 
