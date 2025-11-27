# generate_synthetic.py
"""
Gera um dataset sintético de hemogramas.
Uso:
    python generate_synthetic.py
Saída:
    hemograma_sintetico.csv
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate(n_municipios=8, days=120, records_per_day=5, start_date="2025-01-01"):
    municipios = [f"Municipio_{i+1}" for i in range(n_municipios)]
    start = datetime.fromisoformat(start_date)
    rows = []
    for d in range(days):
        date = (start + timedelta(days=d)).date().isoformat()
        for m in municipios:
            # base mean plaquetas normal ~ 220k, with municipio-specific offset
            base = 220000 + random.randint(-15000, 15000)
            # Simular um surto sintético em Municipio_3 entre day 20 and 40
            if m == "Municipio_3" and 20 <= d <= 40:
                base = int(base * 0.6)  # queda acentuada
            # slight seasonal effect
            if (d % 30) in (5,6,7):
                base = int(base * 0.95)
            for _ in range(records_per_day):
                plaquetas = int(np.random.normal(loc=base, scale=12000))
                plaquetas = max(5000, plaquetas)
                faixa = random.choices(["crianca","jovem","adulto","idoso"], weights=[0.15,0.25,0.45,0.15])[0]
                sexo = random.choice(["M","F"])
                paciente_id = f"{m}_{d}_{random.randint(1,99999)}"
                rows.append({
                    "paciente_id": paciente_id,
                    "municipio": m,
                    "data_coleta": date,
                    "plaquetas": plaquetas,
                    "faixa_etaria": faixa,
                    "sexo": sexo
                })
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate(n_municipios=8, days=120, records_per_day=6, start_date="2025-01-01")
    out = "hemograma_sintetico.csv"
    df.to_csv(out, index=False)
    print(f"Arquivo gerado: {out} ({len(df)} registros)")
