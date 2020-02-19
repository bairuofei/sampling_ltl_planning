# -*- coding: utf-8 -*-
import spot
spot.setup()
a=spot.translate('(GF p23) & (GF p21) & (!p23 U p13)', 'BA','Deterministic')
a.show("v")
print(a.to_str('spin'))


a.save('example.txt').save('example.txt', format='spin', append=False)

