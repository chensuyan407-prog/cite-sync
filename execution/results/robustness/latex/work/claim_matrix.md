# Claim-citation matrix (judge every row; write verdicts into edits.json)

Columns: occurrence | sentence (markers removed) | cited record (title / venue / year) | lexical support hint

## c2_0  (u2s0, body)  `\cite{vaswani2017attention,vaswani2017arxiv}` -> `\cite{vaswani2017attention}`
> Attention-only models were introduced in.
- L1-1 [] Attention is all you need |  | Advances in Neural Information Processing Systems 2017 | support=0.0 terms=[]

## c3_0  (u3s0, body)  `\citep{he2016deep}` -> `\citep{he2016deep}`
> Very deep residual networks and the deep-learning review are standard references.
- L1-4 [] Deep Residual Learning for Image Recognition |  | 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2016 | support=0.38 terms=['deep', 'residual']

## c3_1  (u3s0, body)  `\cite{lecun2015deep}` -> `\cite{lecun2015deep}`
> Very deep residual networks and the deep-learning review are standard references.
- L1-5 [] Deep learning |  | Nature 2015 | support=0.4 terms=['deep']

## c4_0  (u4s0, body)  `\cite{nokey2020}` -> `\cite{nokey2020}`
> A missing key should be reported.
- MISSING-nokey2020 [] 【缺失文献：原稿引用 nokey2020 在参考文献表中找不到，需人工补充】 |  |   | support=0.0 terms=[]

