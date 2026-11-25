# 深度神经网络结构演进简述

## 1 引言

深度学习通过多层表示学习显著提升了语音识别、视觉目标识别等任务的性能[1]。卷积神经网络在 ImageNet 图像分类竞赛中取得突破，大幅降低了 top-5 错误率[2]。随后，残差学习框架使得训练上百层的网络成为可能[3]；同一团队又分析了恒等映射在残差单元中的作用[4]。

## 2 序列建模与注意力

长短期记忆网络通过门控机制缓解了循环网络的梯度消失问题[5]。Transformer 完全基于注意力机制，在机器翻译任务上取得了当时最好的结果[6]。BERT 通过双向预训练显著提升了多项语言理解任务的表现[7]。

已有研究表明，语言模型的测试损失随模型参数量、数据集规模和训练算力呈幂律下降[8]。

## 3 训练技巧

批归一化通过减少内部协变量偏移加速了深层网络训练[9]。Adam 优化器被广泛用于训练上述模型[10]。池化层在卷积神经网络中承担特征降维的作用[11]。

![图1 残差单元结构示意（引自文献[3]）](fig1.png)

## 4 结构生物学中的应用

AlphaFold 能够以接近实验精度预测蛋白质三维结构[12]。另有研究报道残差注意力网络在多个尺度上存在普适的缩放规律。

## 参考文献

[1] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444. DOI:10.1038/nature14539.
[2] Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks[J]. Communications of the ACM, 2017, 60(6): 84-90.
[3] He K, Zhang X, Ren S, et al. Deep Residual Learning for Image Recognition[C]//2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016: 770-778. DOI:10.1109/CVPR.2016.90.
[4] He K, Zhang X, Ren S, et al. Identity mappings in deep residual networks[C]//European Conference on Computer Vision. Springer, 2016: 630-645.
[5] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1785.
[6] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems, 2017: 5998-6008.
[7] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of deep bidirectional transformers for language understanding[C]//Proceedings of NAACL-HLT, 2019: 4171-4186.
[8] Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models[J/OL]. arXiv preprint arXiv:2001.08361, 2020. https://arxiv.org/abs/2001.08361.
[9] Ioffe S, Szegedy C. Batch normalization: Accelerating deep network training by reducing internal covariate shift[C]//International Conference on Machine Learning, 2015: 448-456.
[10] Kingma D P, Ba J. Adam: A method for stochastic optimization[J/OL]. arXiv preprint arXiv:1412.6980, 2014. https://arxiv.org/abs/1412.6980.
[11] 袁铭阳, 周长胜, 黄宏博, 等. 卷积神经网络池化方法综述[J]. 软件工程与应用, 2020, 9(5): 360-372. DOI:10.12677/SEA.2020.95041.
[12] Jumper J, Evans R, Pritzel A, et al. Highly accurate protein structure prediction with AlphaFold[J]. Nature, 2021, 596(7873): 583-589. DOI:10.1038/s41586-021-03819-2.