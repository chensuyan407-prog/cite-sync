# 图神经网络与预训练模型综述（节选）

## 1 背景

图卷积网络将卷积运算推广到图结构数据^[3]^。图注意力网络为邻居节点分配不同的注意力权重^[1]^。在自然语言处理领域，GPT-3 展示了大规模语言模型的少样本学习能力^[2]^，而 BERT 采用掩码语言模型进行双向预训练^[4]^。

## 2 方法

本文采用的优化器为 Adam^[5]^，并在训练中使用 Dropout 防止过拟合^[6]^。相关的图表示学习方法可参见文献^[3-5]^。

实验表明，模型在 Cora 数据集上的准确率达到 83.0%^[7]^。

我们进一步参考了 Transformer 架构^[9]^。

## 参考文献

[1] Veličković P, Cucurull G, Casanova A, et al. Graph attention networks[C]//International Conference on Learning Representations. 2018.
[2] Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[C]//Advances in Neural Information Processing Systems. 2020, 33: 1877-1901.
[3] Kipf T N, Welling M. Semi-supervised classification with graph convolutional networks[J]. arXiv preprint arXiv:1609.02907, 2016.
[4] Devlin J, Chang M W, Lee K, et al. BERT: pre-training of deep bidirectional transformers for language understanding[J]. arXiv preprint arXiv:1810.04805, 2018.
[5] Kingma D P, Ba J. Adam: A method for stochastic optimization[C]//International Conference on Learning Representations. 2015.
[6] Srivastava N, Hinton G, Krizhevsky A, et al. Dropout: a simple way to prevent neural networks from overfitting[J]. Journal of Machine Learning Research, 2014, 15(1): 1929-1958.
[7] Kipf T N, Welling M. Semi-supervised classification with graph convolutional networks[C]//International Conference on Learning Representations. 2017.
[8] Hamilton W L, Ying R, Leskovec J. Inductive representation learning on large graphs[C]//Advances in Neural Information Processing Systems. 2017: 1024-1034.
