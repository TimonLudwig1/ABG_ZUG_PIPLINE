import os
import shutil
import pandas as pd
from dbfread import DBF
from dbfread import DBF, FieldParser
import datetime

class SafeFieldParser(FieldParser):
    """Behandelt fehlerhafte Datumsformate in den DBF-Dateien."""
    def parseD(self, field, data):
        try:
            return super().parseD(field, data)
        except:
            try:
                text = data.decode('latin1').strip()
                for fmt in ('%d.%m.%y', '%d.%m.%Y', '%Y%m%d'):
                    try:
                        return datetime.datetime.strptime(text, fmt).date()
                    except:
                        pass
            except:
                pass
            return None  

def convert_dbf_to_csv(input_file, output_file, encoding='latin1'):
    table = DBF(input_file, encoding=encoding, parserclass=SafeFieldParser)  # ← parserclass hinzugefügt
    df = pd.DataFrame(iter(table))
    if not df.empty:
        df.to_csv(output_file, index=False)
        return True
    return False

def find_dbf_files(base_directory):
    """Alle .dbf-Dateien im Verzeichnis finden und auflisten."""
    dbf_files = []
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.lower().endswith('.dbf'):
                dbf_files.append(os.path.join(root, file))
    return dbf_files

def select_files_interactively(dbf_files):
    """Nutzer wählt Dateien per Nummer aus."""
    print("\nGefundene .dbf-Dateien:")
    for i, f in enumerate(dbf_files):
        print(f"  [{i+1}] {f}")
    
    print("\nAuswahl (Beispiele):")
    print("  '1 3 5'   → Dateien 1, 3 und 5")
    print("  'all'     → alle Dateien")
    print("  'q'       → Abbrechen\n")
    
    choice = input("Ihre Auswahl: ").strip().lower()
    
    if choice == 'q':
        return []
    if choice == 'all':
        return dbf_files
    
    selected = []
    for part in choice.split():
        try:
            idx = int(part) - 1
            if 0 <= idx < len(dbf_files):
                selected.append(dbf_files[idx])
            else:
                print(f"Ungültige Nummer: {part}")
        except ValueError:
            print(f"Ungültige Eingabe: '{part}' ignoriert")
    return selected

def scan_and_convert(base_directory, output_directory, data_output_directory, encoding='latin1'):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(data_output_directory, exist_ok=True)
    
    dbf_files = find_dbf_files(base_directory)
    if not dbf_files:
        print("Keine .dbf-Dateien gefunden.")
        return
    
    selected_files = select_files_interactively(dbf_files)
    if not selected_files:
        print("Keine Dateien ausgewählt.")
        return
    
    for input_file in selected_files:
        file = os.path.basename(input_file)
        output_file = os.path.join(output_directory, os.path.splitext(file)[0] + '.csv')
        data_output_file = os.path.join(data_output_directory, os.path.splitext(file)[0] + '.csv')
        print(f"\nKonvertiere: {input_file}")
        try:
            if convert_dbf_to_csv(input_file, output_file, encoding):
                shutil.move(output_file, data_output_file)
                print(f"Gespeichert: {data_output_file}")
            else:
                print(f"Keine Daten in {input_file}, übersprungen.")
        except UnicodeDecodeError as e:
            print(f"Encoding-Fehler: {e}")
        except Exception as e:
            print(f"Fehler: {e}")

#base_directory = '.'
#output_directory = os.path.join(base_directory, 'converted_csv_files')
#data_output_directory = os.path.join(base_directory, 'data_converted_csv_files')
#scan_and_convert(base_directory, output_directory, data_output_directory)

def run_dbf_pipeline(base_directory="input", output_directory="converted_csv_files", data_output_directory="converted_output", encoding='latin1', files='all'):
    """
    Konvertiert DBF-Dateien zu CSV.
    
    Parameter:
        base_directory       : Ordner mit den .dbf-Dateien
        output_directory     : Temporärer Zwischenordner
        data_output_directory: Zielordner für die CSVs
        encoding             : Zeichenkodierung (Standard: latin1)
        files                : 'all' oder Liste mit Dateinamen z.B. ['Ein1993.dbf', 'Ein1994.dbf']
    
    Rückgabe:
        Liste der erfolgreich konvertierten Dateien
    """
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(data_output_directory, exist_ok=True)

    dbf_files = find_dbf_files(base_directory)
    if not dbf_files:
        print("Keine .dbf-Dateien gefunden.")
        return []

    # Dateiauswahl
    if files == 'all':
        selected_files = dbf_files
    else:
        # Nur die gewünschten Dateien aus der Liste filtern
        selected_files = [f for f in dbf_files if os.path.basename(f) in files]

    converted = []
    for input_file in selected_files:
        file = os.path.basename(input_file)
        output_file = os.path.join(output_directory, os.path.splitext(file)[0] + '.csv')
        data_output_file = os.path.join(data_output_directory, os.path.splitext(file)[0] + '.csv')
        try:
            if convert_dbf_to_csv(input_file, output_file, encoding):
                shutil.move(output_file, data_output_file)
                converted.append(data_output_file)
                print(f"{file} → {data_output_file}")
            else:
                print(f"Keine Daten in {file}, übersprungen.")
        except UnicodeDecodeError as e:
            print(f"Encoding-Fehler bei {file}: {e}")
        except Exception as e:
            print(f"Fehler bei {file}: {e}")

    print(f"\n{len(converted)} Datei(en) konvertiert.")
    return converted

def run_filter_pipeline(base_dir, output_dir=None, jahresbereich=range(1993, 2025)):
    """
    Filtert die konvertierten CSVs auf relevante Spalten.
    
    Parameter:
        base_dir     : Ordner mit den Ein{jahr}.csv Dateien
        output_dir   : Zielordner für gefilterte CSVs (Standard: gleicher Ordner wie base_dir)
        jahresbereich: Welche Jahre verarbeitet werden sollen
    
    Rückgabe:
        Liste der erfolgreich gefilterten Dateien
    """
    if output_dir is None:
        output_dir = base_dir
    os.makedirs(output_dir, exist_ok=True)

    cols = [
        "INVNR", "EINTRART", "AHKN", "AFABMGLN", "BUWERTN",
        "AFAARTN", "ABSCHRBEGN", "ABGDATUM", "TEXT", "JAHRESAFA"
    ]

    filtered = []
    for i in jahresbereich:
        filename = os.path.join(base_dir, f"Ein{i}.csv")
        if not os.path.exists(filename):
            print(f"{filename} nicht gefunden – übersprungen")
            continue

        df = pd.read_csv(filename)
        existing_cols = [c for c in cols if c in df.columns]
        df_new = df[existing_cols].fillna(0)

        output_file = os.path.join(output_dir, f"Ein{i}_filtered.csv")
        df_new.to_csv(output_file, index=False)
        filtered.append(output_file)
        print(f"{output_file} gespeichert")

    print(f"\n{len(filtered)} Datei(en) gefiltert.")
    return filtered

def run_wj_pipeline(base_dir, output_dir=None, jahresbereich=range(1993, 2025), wj_beginn_monat=7):
    """
    Teilt gefilterte CSVs nach Wirtschaftsjahr auf.
    
    Parameter:
        base_dir        : Ordner mit den Ein{jahr}_filtered.csv Dateien
        output_dir      : Zielordner für WJ-CSVs (Standard: base_dir/Wirtschaftsjahre)
        jahresbereich   : Welche Jahre eingelesen werden
        wj_beginn_monat : Startmonat des Wirtschaftsjahres (Standard: 7 = Juli)
    
    Rückgabe:
        Liste der gespeicherten WJ-Dateien
    """
    if output_dir is None:
        output_dir = os.path.join(base_dir, "Wirtschaftsjahre")
    os.makedirs(output_dir, exist_ok=True)

    # Alle gefilterten CSVs einlesen
    all_dfs = []
    for jahr in jahresbereich:
        filename = os.path.join(base_dir, f"Ein{jahr}_filtered.csv")
        if not os.path.exists(filename):
            print(f"{filename} nicht gefunden – übersprungen")
            continue
        df = pd.read_csv(filename)
        all_dfs.append(df)

    if not all_dfs:
        print("Keine Dateien gefunden.")
        return []

    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"\nGesamt: {len(df_all)} Zeilen")

    # Datumsspalten konvertieren
    if "ABSCHRBEGN" in df_all.columns:
        df_all["ABSCHRBEGN"] = pd.to_datetime(df_all["ABSCHRBEGN"], errors="coerce")
    if "ABGDATUM" in df_all.columns:
        df_all["ABGDATUM"] = pd.to_datetime(df_all["ABGDATUM"], errors="coerce")

    # Relevantes Datum je nach EINTRART
    def get_datum(row):
        if str(row.get("EINTRART", "")).strip().upper() == "ABGANG":
            return row["ABGDATUM"]
        else:
            return row["ABSCHRBEGN"]

    df_all["DATUM"] = df_all.apply(get_datum, axis=1)

    fehlend = df_all["DATUM"].isna().sum()
    if fehlend:
        print(f"{fehlend} Zeilen ohne gültiges Datum – werden übersprungen")
    df_all = df_all.dropna(subset=["DATUM"])

    # Wirtschaftsjahr berechnen
    def wirtschaftsjahr(datum):
        if datum.month >= wj_beginn_monat:
            return datum.year
        else:
            return datum.year - 1

    df_all["WJ"] = df_all["DATUM"].apply(wirtschaftsjahr)

    # Nach WJ aufteilen & speichern
    saved = []
    for wj, gruppe in df_all.groupby("WJ"):
        output_file = os.path.join(output_dir, f"WJ_{wj}_{wj+1}.csv")
        gruppe.drop(columns=["DATUM", "WJ"], errors="ignore").to_csv(output_file, index=False)
        saved.append(output_file)
        print(f"WJ {wj}/{wj+1}: {len(gruppe)} Zeilen → {output_file}")

    print(f"\n{len(saved)} Wirtschaftsjahr-Datei(en) gespeichert.")
    return saved