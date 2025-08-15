#!/usr/bin/env python
"""
Script pour créer un fichier Excel d'exemple pour tester l'import.
"""

import pandas as pd
from datetime import date

def create_example_excel():
    # Données d'exemple
    students_data = [
        {
            'Nom': 'DURAND',
            'Prénoms': 'Jean Paul',
            'Date de naissance': '2005-03-15',
            'Lieu de naissance': 'Abidjan',
            'Genre': 'M',
            'Classe': 'Terminale',
            'Section': 'C',
            'Année scolaire': '2024-2025',
            'Pourcentage': 85.5,
            'Rang': 5,
            'Total points': 342,
            'Mention': 'Assez Bien'
        },
        {
            'Nom': 'KOUAME',
            'Prénoms': 'Adjoa Fatou',
            'Date de naissance': '2004-11-20',
            'Lieu de naissance': 'Bouaké',
            'Genre': 'F',
            'Classe': 'Terminale',
            'Section': 'D',
            'Année scolaire': '2024-2025',
            'Pourcentage': 92.3,
            'Rang': 1,
            'Total points': 369,
            'Mention': 'Très Bien'
        },
        {
            'Nom': 'TRAORE',
            'Prénoms': 'Mohamed Issiaka',
            'Date de naissance': '2005-01-08',
            'Lieu de naissance': 'Korhogo',
            'Genre': 'M',
            'Classe': 'Première',
            'Section': 'A',
            'Année scolaire': '2024-2025',
            'Pourcentage': 78.9,
            'Rang': 12,
            'Total points': 315,
            'Mention': 'Assez Bien'
        },
        {
            'Nom': 'BAMBA',
            'Prénoms': 'Aminata Salimata',
            'Date de naissance': '2005-07-03',
            'Lieu de naissance': 'San-Pédro',
            'Genre': 'F',
            'Classe': 'Première',
            'Section': 'C',
            'Année scolaire': '2024-2025',
            'Pourcentage': 88.7,
            'Rang': 3,
            'Total points': 355,
            'Mention': 'Bien'
        },
        {
            'Nom': 'YAO',
            'Prénoms': 'Kofi Emmanuel',
            'Date de naissance': '2004-12-12',
            'Lieu de naissance': 'Yamoussoukro',
            'Genre': 'M',
            'Classe': 'Terminale',
            'Section': 'A',
            'Année scolaire': '2024-2025',
            'Pourcentage': 91.2,
            'Rang': 2,
            'Total points': 365,
            'Mention': 'Très Bien'
        }
    ]
    
    # Créer le DataFrame
    df = pd.DataFrame(students_data)
    
    # Sauvegarder en Excel
    filename = 'example_students.xlsx'
    df.to_excel(filename, index=False, sheet_name='Students')
    
    print(f"✅ Fichier Excel créé: {filename}")
    print(f"📊 {len(students_data)} étudiants ajoutés")
    
    # Afficher un aperçu
    print("\n📋 Aperçu des données:")
    print(df[['Nom', 'Prénoms', 'Classe', 'Section', 'Pourcentage']].to_string(index=False))

if __name__ == '__main__':
    create_example_excel()
