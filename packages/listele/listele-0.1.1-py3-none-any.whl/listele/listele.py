# Bir listenin elemanlarını kolonlar halinde sıralayan fonksiyon:

from sys import stderr

def listele(li:list, kolon:int, ljustmz:int=30, *, find:str=""):
    """ listele(li:list, kolon:int, ljustmz:int=30, *, find:str="")
    """
    try:
        iter(li)
    except:
        print("Listelenemeyen eleman girildi.", file= stderr)
        return

    if find:
        find = find.lower()
        li = [i for i in li if find in i.lower()]

    if not isinstance(kolon, int) or not isinstance(ljustmz, int) or 1 >= kolon > len(li) or ljustmz < 0:
        print("Hatalı parametreler girildi.", file= stderr)
        return

    for i in range(0, len(li)-kolon+1, kolon):
        for j in range(kolon):
            print(str(li[i + j]).ljust(ljustmz), end="")
        print()

    if len(li)%kolon:
        for i in range(len(li)%kolon, 0, -1):
            print(str(li[-i]).ljust(ljustmz), end="")
    print()
