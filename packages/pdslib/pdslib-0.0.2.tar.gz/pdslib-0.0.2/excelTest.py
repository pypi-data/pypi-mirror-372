#-*- coding: utf-8 -*-
import pdslib
import time

def ReadExcel():
    l=pdslib.pglibreadexcel("222222.xlsx")
    print(l.__len__())

def WriteExcel():
    l=[]
    for i in range(1000000):
        l.append(('A', 'B', 'C'))
    print("data alread!")
    pdslib.pgConFigExcel(10,10,10)#行距,字体
    t1=time.time()
    pdslib.pgWriteExcel("222222.xlsx",("a","b"),l,'hhhhh')
    t2=time.time()
    print("write cost time:%fs"  % (t2-t1))


if __name__ ==  '__main__':
    print(pdslib.register("24b0fe586bdab6e7aa692df2d362759cd351af0ae656aa35b890fd3f28d42123fb17bdf2d6c165a0380ce9b63252378fbd792afb52cd60cfd8634211d109a425"))
    t1=time.time()
    WriteExcel()
    t2=time.time()
    ReadExcel()
    t3=time.time()
    print(t3-t2)
    