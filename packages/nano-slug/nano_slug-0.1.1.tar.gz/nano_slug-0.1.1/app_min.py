import sys,re,unicodedata as u
def slug(t):
    t=t.replace('ı','i').replace('İ','i')
    t=u.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    t=re.sub(r'[^a-z0-9]+','-',t).strip('-')
    return t or 'slug'
def main():
    a=' '.join(sys.argv[1:])
    if not a and not sys.stdin.isatty(): a=sys.stdin.read()
    print(slug(a or ''))
if __name__=='__main__': main()
