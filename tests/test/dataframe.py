import pandas as pd



__name__ = "__main__"

data = {"name": ["a", "b"], 
        "age": [10, 30]
        }
df = pd.DataFrame(data)
# print(df)
# df.iloc[0, df.columns.get_loc('age')] = 20
# print(df)
# df.loc[(df['age'] > 20), 'large'] = 1

# print(df)
s = df.iloc[-1].squeeze() # 获取最后一行数据，并转换为Series

print(s['name'])