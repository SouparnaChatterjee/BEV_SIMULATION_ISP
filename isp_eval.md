| degradation   | input           |   features |   inliers |   depth_AbsRel |   ATE_m |   path_len_err_pct |
|:--------------|:----------------|-----------:|----------:|---------------:|--------:|-------------------:|
| clean         | raw (reference) |        433 |       192 |          0     |    0    |                0   |
| clean         | WB+gamma        |        435 |       195 |          0.017 |    5.48 |                6.5 |
| clean         | full ISP        |        451 |       196 |          0.019 |   10.78 |                9.5 |
| night         | raw             |        934 |       304 |          0.093 |   13.41 |              -13.8 |
| night         | WB+gamma        |        870 |       300 |          0.217 |   16.46 |              -25.5 |
| night         | full ISP        |       1020 |       323 |          0.292 |   20.76 |              -39.3 |
| rain          | raw             |        300 |       119 |          0.057 |    7.33 |              -11.1 |
| rain          | WB+gamma        |        301 |       116 |          0.054 |    6.09 |               -7.6 |
| rain          | full ISP        |        305 |       118 |          0.055 |    7.61 |               -2.7 |