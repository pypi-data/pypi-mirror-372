import sys,json
def parse(txt):
    d={}; sec=None
    for L in txt.splitlines():
        l=L.strip()
        if not l or l[0] in ';#': continue
        if l[0]=='[' and l[-1]==']': sec=(l[1:-1].strip() or None); continue
        if '=' in l:
            k,v=(x.strip() for x in l.split('=',1))
            d.setdefault(sec or '',{})[k]=v
    return d

def main():
    a=sys.argv[1:]; p=a[0] if a else None; pick=a[1] if len(a)>1 else None
    txt=(sys.stdin.read() if not p or p=='-' else open(p,encoding='utf-8').read())
    D=parse(txt)
    print(json.dumps(D.get(pick,'') if pick else D, ensure_ascii=False, separators=(',',':')))

if __name__=='__main__': main()
