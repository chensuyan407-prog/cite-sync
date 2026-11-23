# 图神经网络与预训练模型综述（节选）

## 1 背景

图卷积网络将卷积运算推广到图结构数据^[1]^。图注意力网络为邻居节点分配不同的注意力权重^[2]^。在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力^[3]^，而 BERT 采用掩码语言模型进行双向预训练^[4]^。

## 2 方法

本文采用的优化器为 Adam^[5]^，并在训练中使用 Dropout 防止过拟合^[6]^。相关的图表示学习方法可参见文献^[1,4]^。

实验表明，模型在 Cora 数据集上的准确率达到 83.0%^[1]^。

我们进一步参考了 Transformer 架构^[7]^。

## 参考文献

[1] Kipf T N, Welling M. Semi-supervised classification with graph convolutional networks[C]//International Conference on Learning Representations, 2017.
[2] Veličković P, Cucurull G, Casanova A, et al. Graph Attention Networks[C]//International Conference on Learning Representations, 2018.
[3] Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[C]//Advances in Neural Information Processing Systems, 2020: 1877-1901.
[4] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding[C]//Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers). Minneapolis, Minnesota: Association for Computational Linguistics, 2019: 4171-4186. DOI:10.18653/v1/N19-1423.
[5] Kingma D P, Ba J. Adam: A method for stochastic optimization[C]//International Conference on Learning Representations, 2015.
[6] Srivastava N, Hinton G, Krizhevsky A, et al. Dropout: a simple way to prevent neural networks from overfitting[J]. Journal of Machine Learning Research, 2014, 15(1): 1929-1958.
[7] 【缺失文献：原稿引用 9 在参考文献表中找不到，需人工补充】