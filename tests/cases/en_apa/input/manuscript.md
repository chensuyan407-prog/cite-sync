# Why depth works: a short note

Deep learning has transformed speech and visual recognition (LeCun et al., 2015). Residual networks made models with more than a hundred layers trainable (He et al., 2016a), and identity shortcuts further eased optimization (He et al., 2016b). Vaswani et al. (2017) replaced recurrence with attention in the Transformer. Batch normalization accelerates training by reducing internal covariate shift (Ioffe & Szegedy, 2015; Ioffe & Szegedy, 2015). Language-model loss falls as a power law in model size, data and compute (Kaplan et al., 2020). Prior work has shown that dropout prevents overfitting.

## References

He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (pp. 770-778).
He, K., Zhang, X., Ren, S., & Sun, J. (2016). Identity mappings in deep residual networks. In European Conference on Computer Vision (pp. 630-645). Springer.
Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training by reducing internal covariate shift. arXiv preprint arXiv:1502.03167.
Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., Gray, S., Radford, A., Wu, J., & Amodei, D. (2020). Scaling laws for neural language models. arXiv preprint arXiv:2001.08361.
LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521(7553), 436-444. https://doi.org/10.1038/nature14539
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. arXiv preprint arXiv:1706.03762.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. In Advances in Neural Information Processing Systems, 30, 5998-6008.
