import numpy as np
import numpy.random as ra
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as ipw
from IPython.display import display, HTML
from cdsutils.mutils import *
from cdsutils.sdt import *
import random


def pop1(l1,l2,n):
    return ra.uniform(l1,l2,n)

def pop2(l1,l2,n):
    return ra.normal(l1,l2,n)

def pop3(p1, p2, n):
    return ra.rayleigh(p1,n)



def num_pos(data, threshold):
    return len([d for d in data if d >= threshold])
def num_neg(data, threshold):
    return len([d for d in data if d < threshold])
def pf(data, threshold):
    return num_pos(data, threshold)/len(data)
def pops_min(*ps):
    return np.min([np.min(p) for p in ps])
def pops_max(*ps):
    return np.max([np.max(p) for p in ps])

def trace_roc(pos, neg, num=100, delta=0.1):
    mint = pops_min(pos,neg)
    maxt = pops_max(pos,neg)
    
    return ([pf(neg,t) for t in np.linspace(maxt+delta, mint-delta, num=num)],
           [pf(pos,t) for t in np.linspace(maxt+delta, mint-delta, num=num)]
        )
    

def auc_(fpf, tpf):
    auc = 0.0
    for i in range(len(fpf)-1):
        dx = fpf[i+1]-fpf[i]
        y2 = tpf[i+1]
        y1 = tpf[i]
        auc = auc + dx*y1

    return auc
def auc(pos, neg):
    fs, ts = trace_roc(pos, neg)
    return auc_(fs,ts)


def ppv(pos,neg, t):
    try:
        np = num_pos(pos, t)
        return np/(np+num_pos(neg, t))
    except ZeroDivisionError:
        return 1.0
def npv(pos, neg, t):
    try:
        nn = num_neg(neg, t)
        return nn/(nn+num_neg(pos, t))
    except ZeroDivisionError:
        return 1.0

class ExploreStats(ipw.VBox):
    def __init__(self):
        self.p1a = ipw.FloatRangeSlider(min=-5, max=5, value=[-2,2])
        self.p1a.observe(self.a_changed, 'value')
        self.p1b = ipw.FloatRangeSlider(min=-5, max=5, value=[-2,2])
        self.p1b.observe(self.b_changed, 'value')
        self.na = ipw.IntSlider(min=20, max=5000, value=100)
        self.na.observe(self.a_changed, 'value')
        self.nb = ipw.IntSlider(min=20, max=5000, value=100)
        self.nb.observe(self.b_changed, 'value')
        
        self.p2a_μ = ipw.FloatSlider(min=-5, max=5, value=0)
        self.p2a_μ.observe(self.a_changed, 'value')
        self.p2b_μ = ipw.FloatSlider(min=-5, max=5, value=0)
        self.p2b_μ.observe(self.b_changed, 'value')

        self.p2a_σ = ipw.FloatSlider(min=0.5, max=3, value=1)
        self.p2a_σ.observe(self.a_changed, 'value')
        self.p2b_σ = ipw.FloatSlider(min=0.5, max=3, value=1)
        self.p2b_σ.observe(self.b_changed, 'value')
        
        self.t=ipw.FloatSlider()
        self.popsa = ipw.Dropdown(
                        options=["uniform", "gaussian"],
                        value="uniform",
                        description='Number:',
                        disabled=False,
                    )
        self.popsa.observe(self.popa_changed, 'value')
        self.popsb = ipw.Dropdown(
                        options=["uniform", "gaussian"],
                        value="uniform",
                        description='Number:',
                        disabled=False,
                    )
        self.popsb.observe(self.popb_changed, 'value')
        self.p2abox = ipw.VBox([ipw.Label("μ"), self.p2a_μ, ipw.Label("σ"), self.p2a_σ], layout=ipw.Layout(visibility='hidden'))
        self.p2bbox = ipw.VBox([ipw.Label("μ"), self.p2b_μ, ipw.Label("σ"), self.p2b_σ], layout=ipw.Layout(visibility='hidden'))
        
        abox = ipw.VBox([self.popsa, ipw.Label("Number negative cases"), self.na, self.p1a, self.p2abox])
        bbox = ipw.VBox([self.popsb, ipw.Label("Number positive cases"), self.nb, self.p1b, self.p2bbox])
        self.rslts = ipw.HTML()
        self.out1 = ipw.Output()
        
        box = ipw.HBox([self.out1, self.rslts])
        self.neg = pop1(self.p1a.value[0], self.p1a.value[1], self.na.value)
        self.pos = pop1(self.p1b.value[0], self.p1b.value[1], self.nb.value)
        self.set_stats()
        self.t.observe(self._compute_stats, 'value')

        
        super(ExploreStats, self).__init__(children=[ipw.HBox([abox, bbox]), 
                                                     ipw.VBox([ipw.Label("Threshold"), self.t], 
                                                              layout=ipw.Layout(width="100%")), box])
    
    def popa_changed(self, *args):
        if self.popsa.value == "uniform":
            self.p1a.layout.visibility = 'visible'
            self.p2abox.layout.visibility='hidden'
        else:
            self.p1a.layout.visibility = 'hidden'
            self.p2abox.layout.visibility='visible'            
        self.a_changed()
            
    def popb_changed(self, *args):
        if self.popsb.value == "uniform":
            self.p1b.layout.visibility = 'visible'
            self.p2bbox.layout.visibility='hidden'
        else:
            self.p1b.layout.visibility = 'hidden'
            self.p2bbox.layout.visibility='visible'    
        self.b_changed()
        
    def a_changed(self, *args):
        if self.popsa.value == "uniform":
            self.neg = pop1(self.p1a.value[0], self.p1a.value[1], self.na.value)
        else:
            self.neg = pop2(self.p2a_μ.value, self.p2a_σ.value, self.na.value)
        self.set_stats()
        
    def b_changed(self, *args):
        if self.popsb.value == "uniform":
            self.pos = pop1(self.p1b.value[0], self.p1b.value[1], self.nb.value)
        else:
            self.pos = pop2(self.p2b_μ.value, self.p2b_σ.value, self.nb.value)   
        self.set_stats()
        
    def set_stats(self):
        self.prev = len(self.pos)/(len(self.pos)+len(self.neg))
        self.cprev= 1-self.prev
        mint = pops_min(self.pos,self.neg)
        maxt = pops_max(self.pos,self.neg)
        self.t.min = mint+0.5
        self.t.max = maxt-0.5
        self.t.value = (maxt+mint)/2.0
        self.fs,self.ts = trace_roc(self.pos, self.neg)
        self.auc_value = auc_(self.fs,self.ts)
        self._compute_stats()
        
    def _compute_stats(self, *args):
        t = self.t.value
        self.out1.clear_output(wait=True)
        tpf = pf(self.pos,t)
        sens = tpf
        fpf = pf(self.neg,t)
        spec = 1-fpf
        ntp = num_pos(self.pos,t)
        nfn = len(self.pos)-ntp
        ntn = num_neg(self.neg,t)
        nfp = len(self.neg)-ntn
        acc = (ntp+ntn)/(len(self.pos)+len(self.neg))
        _rslts = {"t":"% 3.2f"%t}
        _rslts["ppv"] = "%3.2f"%(ppv(self.pos,self.neg,t))
        _rslts["npv"] = "%3.2f"%(npv(self.pos,self.neg,t))
        _rslts["sens."] = "%3.2f"%tpf
        _rslts["spec."] = "%3.2f"%(1 -fpf)
        _rslts["acc."] = "%3.2f"%(acc)
        _rslts["AUC"] = "%3.2f"%(self.auc_value)
        self.rslts.value = ddict(_rslts, template=dt2)
        with self.out1:
            dot = plt.Circle((fpf,tpf), 0.05, color='red')
            f1,(a1,a2) = plt.subplots(nrows=1, ncols=2)
            a2.plot(self.fs,self.ts)
            sns.distplot(self.neg,ax=a1, kde=False)
            sns.distplot(self.pos,ax=a1, kde=False)
            a1.axvline(t, c='k')
            a2.set_aspect("equal")
            a2.add_artist(dot)
            plt.show(f1)
            
class SensSpecCheck(ipw.VBox):
    def __init__(self, plabel="+", nlabel="-", tol=0.01):
        self._plabel = plabel
        self._nlabel = nlabel
        self._tol = tol
        self.__sens_score = [0.0, 0.0]
        self.__spec_score = [0.0, 0.0]
        self._spec_entry = ipw.Text()
        self._sens_entry = ipw.Text()
        self._sens_score_widget = ipw.HTML("NA")
        self._spec_score_widget = ipw.HTML("NA")
        self._sens_feedback = ipw.HTML()
        self._spec_feedback = ipw.HTML()
        self._check = ipw.Button(description="Check Scores")
        self._check.on_click(self.on_check)
        self._next_case = ipw.Button(description="Generate New Cases")
        self._next_case.on_click(self.binary_test)
        self._df_view = ipw.HTML()
        self._ct_view = ipw.HTML()
        self.binary_test()

        b1 = ipw.HBox(
        [ipw.VBox([self._check, self._sens_score_widget, self._sens_feedback, ipw.Label(value="Sensitivity Estimate"), self._sens_entry]),
         ipw.VBox([self._next_case, self._spec_score_widget, self._spec_feedback, ipw.Label(value="Specificity Estimate"), self._spec_entry])]
        )
        super(SensSpecCheck, self).__init__(children=[b1, ipw.HBox(children=[self._df_view, self._ct_view])])
        
    def binary_test(self, *args):
        n = random.randint(10, 20)
        μ1 = random.uniform(36,37.5)
        μ2 = random.uniform(37, 38.5)
        prevalence = random.uniform(0.2, 0.8)
        
        σ1 = 0.5
        σ2 = 0.5
        
        values = []
        
        for i in range(n):
            if random.random() <= prevalence:
                label = self._plabel
                value = random.gauss(μ2,σ2)
            else:
                label = self._nlabel
                value = random.gauss(μ1, σ1)
            values.append({"case":i, "value":value, "true_label":label})
        self._df = pd.DataFrame(values)
        
        threshold = random.uniform(self._df.value.min(),self._df.value.max())
        self._df["test_label"] = self._df.value.apply(lambda x: self._plabel if x >= threshold else self._nlabel)
        self._df_view.value = self._df.to_html()
    
    def on_check(self, b):
        
        self.check_sensitivity()
        self.check_specificity()
        self.display_scores()
        if self._sens_correct and self._spec_correct:
            self.binary_test()
            
    
    def check_sensitivity(self):

        num_pos = len([1 for _, row in self._df.iterrows() if row["true_label"] == self._plabel ])
        test_pos= len([1 for _, row in self._df.iterrows() if row["true_label"] == self._plabel and row["test_label"] == self._plabel])

        sens = test_pos/num_pos

        self.__sens_score[1] += 1
        if abs(sens-float(eval(self._sens_entry.value))) < self._tol:
            self.__sens_score[0] += 1
            self._sens_feedback.value = "Correct!"
            self._sens_correct = True
        else:
            self._sens_feedback.value = "Your answer differs from the true value by more than %0.2f"%self._tol
            self._sens_correct=False
    
    def check_specificity(self):

        num_neg = len([1 for _, row in self._df.iterrows() if row["true_label"] == self._nlabel ])
        test_neg= len([1 for _, row in self._df.iterrows() if row["true_label"] == self._nlabel and row["test_label"] == self._nlabel])
        spec = test_neg/num_neg

        self.__spec_score[1] += 1
        if abs(spec-float(eval(self._spec_entry.value))) < self._tol:
            self.__spec_score[0] += 1
            self._spec_feedback.value = "Correct!"
            self._spec_correct=True
        else:
            self._spec_feedback.value = "Your answer differs from the true value by more than %0.2f"%self._tol    
            self._spec_correct=False



    def reset_scores(self):
        self.__sens_score = [0.0, 0.0]
        self.__spec_score = [0.0, 0.0]
        self._sens_score_widget.value = "NA"
        self._spec_score_widget.value = "NA"


    def display_scores(self):
        sens = self.__sens_score[0] / self.__sens_score[1]
        spec = self.__spec_score[0] / self.__spec_score[1]

        self._sens_score_widget.value =  """<p>Sens. correct: %3.1f</p>"""%(sens*100)
        self._spec_score_widget.value =  """<p>Spec. correct: %3.1f</p>"""%(spec*100)

class SensSpecCheck2(SensSpecCheck):
    def binary_test(self, *args):
        n = random.randint(10, 20)
        μ1 = random.uniform(36,37.5)
        μ2 = random.uniform(37, 38.5)
        prevalence = random.uniform(0.2, 0.8)
        
        σ1 = 0.5
        σ2 = 0.5
        
        values = []
        
        for i in range(n):
            if random.random() <= prevalence:
                label = self._plabel
                value = random.gauss(μ2,σ2)
            else:
                label = self._nlabel
                value = random.gauss(μ1, σ1)
            values.append({"case":i, "value":value, "true_label":label})
        self._df = pd.DataFrame(values)
        
        threshold = random.uniform(self._df.value.min(),self._df.value.max())
        self._df["test_label"] = self._df.value.apply(lambda x: self._plabel if x >= threshold else self._nlabel)
        self._df_view.value = self._df.to_html()
        self._ct_view.value = pd.crosstab(self._df["true_label"], self._df["test_label"]).to_html()
    
