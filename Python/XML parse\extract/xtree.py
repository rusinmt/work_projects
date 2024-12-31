import xml.etree.ElementTree as ET
import pandas as pd
import os
import re

def parse_nakazy_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespaces = {
        'curr': 'http://www.currenda.pl/epu'
    }
    results = []
    nakaz_epu_elements = root.findall('.//curr:NakazEPU', namespaces)
    print(f"Found {len(nakaz_epu_elements)} NakazEPU elements")

    for nakaz_epu in nakaz_epu_elements:
        kod = nakaz_epu.get('KOD')
        dluznik = nakaz_epu.find('curr:ListaPozwanych', namespaces)
        nazwa = dluznik.find('curr:Pozwany', namespaces)
        name = nazwa.find('curr:Nazwa', namespaces)
        name = name.text if name is not None else None
        sygnatura = nakaz_epu.find('curr:Sygnatura', namespaces)
        sygnatura_text = re.sub(r'\s+', ' ', sygnatura.text) if sygnatura is not None else None
        lista_roszczen = nakaz_epu.find('curr:ListaRoszczen', namespaces)
        
        if lista_roszczen is not None:
            roszczenie_elements = lista_roszczen.findall('curr:Roszczenie', namespaces)
            
            if roszczenie_elements:
                first_roszczenie = roszczenie_elements[0]
                last_roszczenie = roszczenie_elements[-1]
                
                first_wartosc = first_roszczenie.get('wartosc')
                last_wartosc = last_roszczenie.get('wartosc')
            else:
                first_wartosc = None
                last_wartosc = None
        else:
            first_wartosc = None
            last_wartosc = None

        results.append({
            'Sygnatura': sygnatura_text,
            'Kod': kod,
            'Pierwsza wartość': first_wartosc,
            'Ostatnia wartość': last_wartosc,
            'Dane dłużnika': name
        })

    df = pd.DataFrame(results)
    return df

file_paths = [f for f in os.listdir(r"C:\Users\Mateusz\Downloads\Nakazy") if f.lower().endswith('.xml')]
all_dataframes = []
for file_name in file_paths:
    file_path = os.path.join(r"C:\Users\Mateusz\Downloads\Nakazy", file_name)
    df = parse_nakazy_xml(file_path)    
    if not df.empty:
        all_dataframes.append(df)

    if all_dataframes:
        result_df = pd.concat(all_dataframes, ignore_index=True)
        result_df.to_csv(r"C:\Users\Mateusz\Desktop\nakazy.csv", sep=';', encoding='cp1250', index=False)
