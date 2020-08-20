from IPython.display import HTML, display
import json
import sqlite3 as sq
import os
import shutil
import datetime
import markdown
import ipywidgets as ipw
import random
import gzip

try:
    username = os.environ["JUPYTERHUB_USER"]
except KeyError:
    username = 'unknown'

imgs=\
"""
<table>
   <tr>
      <td><img src="./media/ISIC_0000019.jpg" alt="a" width="256"></td>
      <td><img src="./media/ISIC_0000029.jpg" alt="b" width="256"></td>
   </tr>
   <tr>
      <td style="text-align:center">a</td><td style="text-align:center">b</td
      >
   </tr>
    <tr>
      <td><img src="./media/ISIC_0000049.jpg" alt="c" width="256"></td>
      <td><img src="./media/ISIC_0000000.jpg" alt="d" width="256"></td>
    </tr>
   <tr>
      <td style="text-align:center">c</td><td style="text-align:center">d</td>
   </tr>
</table>
"""

class AFC4(ipw.VBox):
    DDIR = ".mydata"
    fname = ".mydata/mydata.json.gz"
    SDIR = "/home/shared/.nevi" 


    def __init__(self, user):
        self.user = user
        if not os.path.exists(self.DDIR):
            os.mkdir(self.DDIR)
        if not os.path.exists(self.fname):
            with gzip.open("user_descriptions.json.gz", "rt", encoding="utf-8") as f:
                responses = json.load(f)
            with gzip.open(self.fname, "wt", encoding='utf-8') as f:
                json.dump(responses, f)
        self.__mapping = {"a":"452914", "b":"452913", "c":"452915", "d":"452912"}
                
        self.score = 0.0
        self.count = 0
        self.instructions = ipw.HTML("<h2>Select the image being described by the text</h2>")
        self.info = ipw.Label(value="")
        self.choices = ipw.Dropdown(options=['a', 'b', 'c', 'd'])
        self.submit = ipw.Button(description="submit")
        self.submit.on_click(self.on_submit)
        self.__imgs = ipw.HTML(imgs)
        self.__get_response()
        self.__desc = ipw.HTML(markdown.markdown(self.__current_case["description"]))

        self.num_remain = len(self.__cases)
        super(AFC4, self).__init__(children=[self.instructions, self.info, self.__imgs, self.__desc, self.choices, self.submit])
        
    def on_submit(self, *args):
        if self.submit.description == 'submit':
            self.submit.description= 'continue'
            self.count += 1
            self.submit_answer()

            if self.__current_case["case"] == self.choices.value:
                feedback = "Correct!"
                self.score += 1
            else:
                feedback = "Incorrect. (Correct case was %s)"%self.__current_case["case"]
            self.info.value = "%s. %d/%d (%3.2f). %d cases remaining"%(feedback,
                                                                    self.score, self.count,
                                                                    self.score/self.count, 
                                                                    len(self.__cases))
            with gzip.open(self.fname, "wt", encoding='utf-8') as f:
                json.dump(self.__cases, f)
        else:
            self.submit.description = 'submit'
            self.__get_response()
            self.__desc.value = markdown.markdown(self.__current_case["description"])
        
    def submit_answer(self):
        conn = sq.connect(os.path.join(self.SDIR, "nevi_fac.sqlite"))
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO results (user,
                                               num,
                                               actual_img,
                                               choice,
                                               ts) 
                                      VALUES (?,?,?,?,?)""",
                      (self.user, self.__current_case["num"], self.__current_case["case"], self.choices.value, datetime.datetime.now()))
        conn.commit()
        conn.close()
    def __get_response(self):
        with gzip.open(self.fname, "rt", encoding='utf-8') as f:
            self.__cases = json.load(f)
            random.shuffle(self.__cases)
        self.__current_case = self.__cases.pop()

