import pandas as pd
import json

# Ler o arquivo CSV
df = pd.read_csv('report.csv')

# Converter para JSON
json_data = df.to_json(orient='records')

# Escrever o JSON em um arquivo
with open('report.json', 'w') as json_file:
    json_file.write(json_data)

print("Arquivo convertido com sucesso!")
