import sys,csv,json,io
def main():
 a=sys.argv[1:];nh=a and a[0]in('-n','--no-header');a=a[1:]if nh else a
 p=a[0]if a else None
 f=open(p,'r',encoding='utf-8',newline='')if p and p!='-' else sys.stdin
 t=f.read()if f is sys.stdin else None
 if t is None:s=f.read(4096);f.seek(0)
 else:s=t[:4096];f=io.StringIO(t)
 try:d=csv.Sniffer().sniff(s)
 except:d=csv.excel
 has=(not nh)and csv.Sniffer().has_header(s)
 R=csv.DictReader(f,dialect=d)if has else csv.reader(f,dialect=d)
 for r in R:
  if has:print(json.dumps(r,ensure_ascii=False))
  else:print(json.dumps({f'c{i+1}':v for i,v in enumerate(r)},ensure_ascii=False))
if __name__=='__main__':main()
