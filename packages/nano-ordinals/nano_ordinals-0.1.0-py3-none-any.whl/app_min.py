import re,sys
def o(n):
 n=int(n); s='-' if n<0 else ''; n=abs(n)
 return f"{s}{n}{'th' if 10<n%100<14 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def c(s):
 m=re.match(r'\s*([+-]?\d+)(?:st|nd|rd|th)?\s*$',s.lower())
 return int(m.group(1)) if m else None
def main():
 a=' '.join(sys.argv[1:]).strip()
 print(c(a) if re.search('[a-zA-Z]',a) else o(a))
if __name__=='__main__': main()
