import datetime as dt

import sf_quant as sf

start = dt.date(2024, 1, 1)
end = dt.date(2024, 12, 31)

columns = ["date", "barrid", "ticker", "price", "return"]

df = sf.data.assets.load(start=start, end=end, in_universe=True, columns=columns)

print(df)
