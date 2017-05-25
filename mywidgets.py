import ipywidgets as wg
from IPython.display import display
ageRange = wg.IntRangeSlider(value=[55, 64], min=0, max=110, step=1, description='Age Range:')
readFiles = wg.SelectMultiple(options=["all", "diary", "interview", "dtbd", "expd", "fmld", "memd", "fmli", "itbi", "memi", "mtbi","ntaxi"], value=['fmli','mtbi'],description='Files to Read:')
