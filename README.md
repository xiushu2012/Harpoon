# harpoon 和 cartridge 的使用说明
0.所有的投入前提都是以胜为前提，“是故胜兵先胜而后求战”

1.先使用harpoon过滤出价格（低）和市值（小）和价值距离（近）都满足
要求的备选可转债，备选的可转债需要有至少一年的交易时常，来遍历各种涨跌情况

2.使用cartridge计算可转债的胜率,赔率和下注比例，下注时把总投入规模
平均分给每个预投标的，然后每个可转债按照下注比例f独立下注，例如预期投入
15w给5个可转债，那么每个可转债的下注额= 3w*f,注意剩余部分一般不相互
拆借，如果有一个首先退出（包括赢和输）那么，新下注时按照总资产再次计算
预期每一个的投入

3.追加下注时，按照当前下注比例进行计算，然后减去已投入部分

4.按照以上方式源源不断的产生现金流使得整个过程能够持续下去