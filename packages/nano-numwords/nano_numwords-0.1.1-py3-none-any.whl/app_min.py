import re,sys
U="zero one two three four five six seven eight nine".split()
W={w:i for i,w in enumerate(U)}
W.update(dict(zip("ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),range(10,20))))
W.update({w:(i+2)*10 for i,w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())})
S={w:1000**(i+1) for i,w in enumerate("thousand million billion trillion quadrillion quintillion sextillion septillion octillion nonillion decillion".split())}
def n(x):
  t=re.findall("[a-z]+",x.lower().replace("-"," ")); s=-1 if t and t[0]in("minus","negative")else 1; t=t[1:]if s<0 else t; T=G=i=0
  while i<len(t):
    w=t[i]
    if w=="point":
      i+=1; q=1.0; y=0.0
      while i<len(t): q*=10; y+=W.get(t[i],0)/q; i+=1
      return s*(T+G+y)
    if w in S: T+=G*S[w]; G=0; i+=1; continue
    if w=="hundred": G=(G or 1)*100; i+=1; continue
    v=W.get(w)
    if v is None:
      if w.endswith("teen"): v=10+W.get(w[:-4].replace("thir","three").replace("fif","five").replace("twel","twelve").replace("eigh","eight"),0)
      elif w.endswith("ty"): v=10*W.get(w[:-2].replace("twen","two").replace("thir","three").replace("fif","five").replace("eigh","eight").replace("for","four"),0)
      else: v=0
    G+=v; i+=1
  return s*(T+G)

def main():
  print(n(" ".join(sys.argv[1:])))

if __name__=="__main__":
  main()
