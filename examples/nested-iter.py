"""A small example showing the use of nested iterators within PyTables.

This program needs the output file, 'tutorial1.h5', generated by
'tutorial1-1.py' in order to work.

"""

import tables
f=tables.openFile("tutorial1.h5")
rout = f.root.detector.readout

print "*** Result of a three-folded nested iterator ***"
for p in rout.where(rout.cols.pressure < 16):
    for q in rout.where(rout.cols.pressure < 9):
        for n in rout.where(rout.cols.energy < 10):
            print "pressure, energy-->", p['pressure'],n['energy']
print "*** End of selected data ***"
f.close()
