import sys
S="M CM D CD C XC L XL X IX V IV I".split();V=[1000,900,500,400,100,90,50,40,10,9,5,4,1];T=list(zip(S,V))
def i2r(n):
    s=""
    for k,v in T:
        q,n=divmod(int(n),v); s+=k*q
    return s
def r2i(s):
    s=s.upper(); i=n=0
    for k,v in T:
        L=len(k)
        while s[i:i+L]==k:
            n+=v; i+=L
            if i>=len(s): break
        if i>=len(s): break
    return n
def main():
    a=" ".join(sys.argv[1:])
    if not a: return print("usage: nano-roman <number|ROMAN>")
    print(i2r(a) if a.isdigit() else r2i(a))
if __name__=="__main__": main()
