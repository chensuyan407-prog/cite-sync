# Claim-citation matrix (judge every row; write verdicts into edits.json)

Columns: occurrence | sentence (markers removed) | cited record (title / venue / year) | lexical support hint

## c2_0  (u2s0, body)  `[2]` -> `[1]`
> 深度学习综述见文献。
- M2 [1] Deep learning |  | Nature 2015 | support=0.8 terms=['deep', 'learning']

## c2_1  (u2s1, body)  `[1-2]` -> `[1,2]`
> 长短期记忆网络见。
- M1 [2] Long short-term memory |  | Neural Computation 1997 | support=0.85 terms=['long', 'memory', 'short-term']
- M2 [1] Deep learning |  | Nature 2015 | support=0.0 terms=[]

## c2_2  (u2s2, body)  `[7]` -> `[3]`
> 另见。
- MISSING-7 [3] 【缺失文献：原稿引用 7 在参考文献表中找不到，需人工补充】 |  |   | support=0.0 terms=[]

