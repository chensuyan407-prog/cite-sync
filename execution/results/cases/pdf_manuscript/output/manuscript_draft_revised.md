Notes on training and scaling deep networks

## 1 Background

Residual learning lets networks with more than 100 layers be trained and won the ILSVRC 2015 classification task [1]. Batch normalization normalizes layer inputs over each mini-batch and allows much higher learning rates [2]. The Transformer relies entirely on attention and dispenses with recurrence and convolutions [3].

## 2 Scaling

The test loss of language models scales as a power law with model size, dataset size and the amount of compute used for training [1]. Larger models are significantly more sample-efficient [4]. It has been shown that dropout reduces overfitting in large networks.

## References

[1] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2016: 770-778. DOI:10.1109/cvpr.2016.90.
[2] Ioffe S, Szegedy C. Batch normalization: Accelerating deep network training by reducing internal covariate shift[C]//International Conference on Machine Learning, 2015: 448-456.
[3] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems, 2017: 5998-6008.
[4] Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models[J/OL]. arXiv preprint arXiv:2001.08361, 2020. https://arxiv.org/abs/2001.08361.