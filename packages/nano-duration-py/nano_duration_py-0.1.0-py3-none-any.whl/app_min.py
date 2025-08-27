import re,sys
def to_sec(s):return sum(int(n)*{'h':3600,'m':60,'s':1}[u]for n,u in re.findall(r'(\d+)\s*([hms])',s.lower()))
def fmt(x):
 x=int(x);h,x=divmod(x,3600);m,x=divmod(x,60)
 return(f'{h}h'if h else'')+(f'{m}m'if m else'')+(f'{x}s'if x or(not h and not m) else'')
def main():
 a=' '.join(sys.argv[1:]).strip()
 print(fmt(a)if a.lstrip('-').isdigit() else to_sec(a))
if __name__=='__main__':main()
