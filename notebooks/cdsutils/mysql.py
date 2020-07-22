from .mutils import *


def get_mimic_connection():
    return \
    ibis.mysql.connect(
    user="jovyan",
    password="jovyan",
    host="35.233.174.193",
    port=3306,
    database='mimic2')

def tview(t,start):
    display(t.limit(5, offset=start).execute())
def itview(t):
    nrows = t.count().execute()
    ipw.interact(tview, t=ipw.fixed(t), 
                 start=ipw.IntSlider(min=0, max=nrows, value=0))


def view_table(table, conn):
    t = conn.table(table)
    nrows = t.count().execute()
    @interact(t=fixed(t), num=ipw.IntSlider(min=5, max=20), 
              start=ipw.IntSlider(min=0, max=nrows))
    def _view_table(t, num, start=0):
        return t.limit(num, offset=start).execute()
    

