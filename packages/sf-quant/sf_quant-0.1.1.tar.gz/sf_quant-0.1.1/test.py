import datetime as dt

import sf_quant as sf

start = dt.date(2024, 1, 1)
end = dt.date(2024, 12, 31)

columns = [
    'date',
    'permno',
    'ticker',
    'ret',
    'prc'
]

df = sf.data.crsp_monthly.load(
    start=start, 
    end=end, 
    columns=columns
)

print(df)
