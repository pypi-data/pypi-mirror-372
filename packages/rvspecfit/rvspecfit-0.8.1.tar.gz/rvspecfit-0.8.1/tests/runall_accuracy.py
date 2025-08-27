import os
os.environ['OMP_NUM_THREADS'] = '1'
import multiprocessing as mp
import numpy as np
import sys
import accuracy

if __name__ == '__main__':
    np.random.seed(1)
    if len(sys.argv) > 1:
        sn = int(sys.argv[1])
    else:
        sn = 300
    nthreads = 24
    nlam = 400
    resol = 1000
    nit = 1000
    xs = np.random.randint(0, int(1e9), size=nit)

    if nthreads > 1:
        poo = mp.Pool(nthreads)
    ret = []
    for i in xs:
        kw = dict(sn=sn, nlam=nlam, resol=resol)
        args = (i, )
        if nthreads > 1:
            ret.append(poo.apply_async(accuracy.doone, args, kw))
        else:
            ret.append(accuracy.doone(*args, **kw))
    if nthreads > 1:
        ret = [_.get() for _ in ret]
    v0, v1, err = np.array(ret).T

    ##for i in range(nit):
    #    print (v0[i],v1[i],err[i])
    dx = v1 - v0
    xind = (err < np.median(err))
    print(np.median(dx), np.median(err), np.std(dx), np.std(dx / err))
    print(np.median(dx[xind]), np.median(err[xind]), np.std(dx[xind]))
    poo.close()
    poo.join()
