import pandas as pd
import plotly.express as px
import main as m

df = pd.DataFrame(dict(
  y =  [1, 3, 4, 5, 1, 2],
  x = [1 ,2 ,3 ,4 ,5 ,6],
  z = [6,5,4,3,2,1]
))

fig = px.line_3d(df, x="x", y="y", z = "z", title="Voorbeeld")
fig.show()