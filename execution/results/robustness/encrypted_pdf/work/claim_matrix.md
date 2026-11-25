# Claim-citation matrix (judge every row; write verdicts into edits.json)

Columns: occurrence | sentence (markers removed) | cited record (title / venue / year) | lexical support hint

## c4_0  (u4s0, body)  `[3]` -> `[1]`
> 深度学习通过多层表示学习显著提升了语音识别、视觉目标识别等任务的性能。
- L1-5 [1] Deep learning |  | Nature 2015 | support=0.8 terms=['deep', 'learning']

## c4_1  (u4s1, body)  `[5]` -> `[2]`
> 卷积神经网络在 ImageNet 图像分类竞赛中取得突破，大幅降低了 top-5 错误率。
- M5 [2] ImageNet classification with deep convolutional neural networks |  | Communications of the ACM 2017 | support=0.833 terms=['classification', 'convolutional', 'imagenet', 'networks', 'neural']

## c4_2  (u4s2, body)  `[1]` -> `[3]`
> 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。
- L1-4 [3] Deep Residual Learning for Image Recognition |  | 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2016 | support=0.57 terms=['deep', 'learning', 'residual']

## c4_3  (u4s2, body)  `[2]` -> `[4]`
> 随后，残差学习框架使得训练上百层的网络成为可能；同一团队又分析了恒等映射在残差单元中的作用。
- M2 [4] Identity mappings in deep residual networks |  | European Conference on Computer Vision. Springer 2016 | support=0.76 terms=['deep', 'identity', 'mappings', 'residual']

## ins_u8s0  (u8s0, body)  `` -> `[5]`
> 长短期记忆网络通过门控机制缓解了循环网络的梯度消失问题。
- M4 [5] Long short-term memory |  | Neural Computation 1997 | support=0.85 terms=None

## ins_u8s1  (u8s1, body)  `` -> `[6]`
> Transformer 完全基于注意力机制，在机器翻译任务上取得了当时最好的结果。
- L1-1 [6] Attention is all you need |  | Advances in Neural Information Processing Systems 2017 | support=0.9 terms=None

## c8_0  (u8s2, body)  `[4][7][9]` -> `[7]`
> BERT 通过双向预训练显著提升了多项语言理解任务的表现。
- M9 [7] BERT: Pre-training of deep bidirectional transformers for language understanding |  | Proceedings of NAACL-HLT 2019 | support=0.75 terms=['bert', 'bidirectional', 'language', 'pre-training', 'understanding']

## c14_0  (u14s0, body)  `[6,8]` -> `[8]`
> 批归一化通过减少内部协变量偏移加速了深层网络训练。
- M6 [8] Batch normalization: Accelerating deep network training by reducing internal covariate shift |  | International Conference on Machine Learning 2015 | support=0.79 terms=['accelerating', 'batch', 'covariate', 'deep', 'normalization', 'shift', 'training']

## c14_1  (u14s1, body)  `<sup>[10]</sup>` -> `[9]`
> Adam 优化器被广泛用于训练上述模型。
- M10 [9] Adam: A method for stochastic optimization |  | arXiv preprint arXiv:1412.6980 2014 | support=0.675 terms=['adam', 'optimization', 'stochastic']

## c14_2  (u14s2, body)  `[12]` -> `[10]`
> 池化层在卷积神经网络中承担特征降维的作用。
- M12 [10] 卷积神经网络池化方法综述 |  | 软件工程与应用 2020 | support=0.682 terms=['卷积', '池化', '神经', '积神', '经网', '网络']

## c16_0  (u16s0, caption)  `[1]` -> `[3]`
> ![图1 残差单元结构示意（引自文献）](fig1.png)
- L1-4 [3] Deep Residual Learning for Image Recognition |  | 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2016 | support=0.19 terms=['residual']

## c20_0  (u20s0, body)  `[11]` -> `[11]`
> AlphaFold 能够以接近实验精度预测蛋白质三维结构。
- M11 [11] Highly accurate protein structure prediction with AlphaFold |  | Nature 2021 | support=0.667 terms=['accurate', 'alphafold', 'protein', 'structure']

## c20_1  (u20s1, body)  `[14]` -> `[12]`
> 另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。
- M14 [12] Universal scaling of residual attention networks |  | Nature 2019 | support=0.57 terms=['attention', 'residual', 'scaling']

# Sentences that look like claims but carry no citation

- u10s0 (cue: 已有研究): 已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训练算力呈幂律下降。
