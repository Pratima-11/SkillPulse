"""Train SkillPulse's reliability model on an explicitly synthetic dataset.

This pipeline is reproducible and intentionally does not claim production data.
It trains a small logistic-regression classifier with pure Python so the model
can be regenerated even in a minimal environment.
"""
from __future__ import annotations
import csv, math, os, pickle, random
from statistics import mean

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
MODEL_DIR = os.path.join(BASE, "models")
os.makedirs(DATA_DIR, exist_ok=True); os.makedirs(MODEL_DIR, exist_ok=True)
DATA_PATH = os.path.join(DATA_DIR, "reliability_training.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "reliability_model.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

FEATURES = ["jobs_completed","jobs_accepted","jobs_cancelled","average_rating","experience_years"]

def sigmoid(z):
    z = max(-30.0, min(30.0, z))
    return 1.0/(1.0+math.exp(-z))

def standardize(rows):
    means=[mean(r[i] for r in rows) for i in range(len(FEATURES))]
    stds=[]
    for i,m in enumerate(means):
        v=mean((r[i]-m)**2 for r in rows)
        stds.append(math.sqrt(v) or 1.0)
    return means,stds

def transform(row, means, stds):
    return [(x-m)/s for x,m,s in zip(row,means,stds)]

def generate(seed=20260927, n=1800):
    rng=random.Random(seed); rows=[]
    for _ in range(n):
        accepted=rng.randint(0,60)
        completed=rng.randint(0,accepted)
        cancelled=rng.randint(0,max(0,accepted-completed)+3)
        rating=round(rng.uniform(2.5,5.0),2) if accepted else round(rng.uniform(0,5),2)
        exp=round(rng.uniform(0,15),1)
        completion_rate=completed/max(1,accepted)
        cancel_rate=cancelled/max(1,accepted+cancelled)
        latent=(2.8*completion_rate + 0.9*(rating/5) + 0.35*min(exp/10,1) - 2.1*cancel_rate)
        latent += rng.gauss(0,0.22)
        label=1 if latent >= 1.0 else 0
        rows.append(([completed,accepted,cancelled,rating,exp],label))
    rng.shuffle(rows)
    return rows

def train(X,y,epochs=2500,lr=0.045):
    means,stds=standardize(X); Z=[transform(x,means,stds) for x in X]
    w=[0.0]*len(FEATURES); b=0.0
    for _ in range(epochs):
        gw=[0.0]*len(w); gb=0.0
        for x,t in zip(Z,y):
            p=sigmoid(sum(a*c for a,c in zip(w,x))+b); e=p-t
            for i,c in enumerate(x): gw[i]+=e*c
            gb+=e
        n=len(Z)
        for i in range(len(w)): w[i]-=lr*gw[i]/n
        b-=lr*gb/n
    return {"type":"logistic_regression","features":FEATURES,"means":means,"stds":stds,"weights":w,"bias":b}

def predict(model,row):
    z=sum(w*x for w,x in zip(model["weights"],transform(row,model["means"],model["stds"])))+model["bias"]
    return sigmoid(z)

def metrics(y,preds,threshold=.5):
    labels=[1 if p>=threshold else 0 for p in preds]
    tp=sum(t==1 and p==1 for t,p in zip(y,labels)); tn=sum(t==0 and p==0 for t,p in zip(y,labels))
    fp=sum(t==0 and p==1 for t,p in zip(y,labels)); fn=sum(t==1 and p==0 for t,p in zip(y,labels))
    accuracy=(tp+tn)/len(y); precision=tp/max(1,tp+fp); recall=tp/max(1,tp+fn); f1=2*precision*recall/max(1e-12,precision+recall)
    return {"accuracy":round(accuracy,4),"precision":round(precision,4),"recall":round(recall,4),"f1":round(f1,4),"confusion_matrix":{"tn":tn,"fp":fp,"fn":fn,"tp":tp}}

def main():
    rows=generate(); split=int(len(rows)*0.8); train_rows=rows[:split]; test_rows=rows[split:]
    X=[r[0] for r in train_rows]; y=[r[1] for r in train_rows]
    model=train(X,y)
    with open(DATA_PATH,"w",newline="") as f:
        w=csv.writer(f); w.writerow(FEATURES+["reliable_label"])
        for features,label in rows: w.writerow(features+[label])
    with open(MODEL_PATH,"wb") as f: pickle.dump(model,f)
    test_preds=[predict(model,r[0]) for r in test_rows]
    m=metrics([r[1] for r in test_rows],test_preds)
    import json
    payload={"dataset":"synthetic SkillPulse reliability scenarios","rows":len(rows),"train_rows":len(train_rows),"test_rows":len(test_rows),"seed":20260927,"features":FEATURES,"target":"reliable_worker","metrics":m,"limitations":["Synthetic data is not production behaviour.","The model should be retrained with consented historical SkillPulse outcomes before deployment."]}
    with open(METRICS_PATH,"w") as f: json.dump(payload,f,indent=2)
    print(json.dumps(payload,indent=2))

if __name__=="__main__": main()
