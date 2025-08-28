import sys
D="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def conv(n,b):
 s='-' if n<0 else ''; n=abs(n);
 if n==0:return '0'
 r=""
 while n:n,rem=divmod(n,b); r=D[rem]+r
 return s+r
def main():
 a=sys.argv[1:]
 if len(a)==2:v,fb,tb=a[0],10,int(a[1])
 elif len(a)==3:v,fb,tb=a[0],int(a[1]),int(a[2])
 else:return print("usage: nano-base <value> <to_base> | nano-base <value> <from_base> <to_base>")
 v=v.upper()
 print(conv(int(v,fb),tb))
if __name__=="__main__":main()
