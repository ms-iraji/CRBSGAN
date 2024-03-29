# Image Classification with Consistency-Regularized Bad Semi-Supervised Generative Adversarial Networks: A Visual Data Analysis and Synthesis

This repository contains the implementation of the CRBSGAN (Consistency-Regularized Bad Semi-Supervised Generative Adversarial Networks) algorithm for image classification:A visual data analysis and synthesis. The CRBSGAN algorithm aims to improve the performance of semi-supervised learning by addressing issues such as incorrect decision boundaries and wrong pseudo-labels for unlabeled images.

## Table of Contents
- [Introduction](#introduction)
- [Authors](#authors)
- [Abstract](#abstract)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Semi-supervised learning has gained significant attention in the field of machine learning due to its potential to improve classification performance. However, traditional semi-supervised learning methods often suffer from incorrect decision boundaries and inaccurate pseudo-labels, leading to decreased generalization performance. The CRBSGAN algorithm addresses these challenges by incorporating consistency regularization and a bad generative adversarial network.

## Authors

- Mohammad Saber Iraji (iraji.ms@gmail.com)
- Jafar Tanha (Corresponding author: tanha@tabrizu.ac.ir, jafar.tanha.pnu@gmail.com)
- Mohammad-Ali Balafar
- Mohammad-Reza Feizi-Derakhshi

This work was conducted by researchers from the Department of Computer Engineering, Faculty of Electrical and Computer Engineering, University of Tabriz, Tabriz, Iran.

## Abstract

Semi-supervised learning, which entails training a model with manually labeled images and pseudo-labels for unlabeled images, has garnered considerable attention for its potential to improve image classification performance. Nevertheless, incorrect decision boundaries of classifiers and wrong pseudo labels for beneficial unlabeled images below the confidence threshold increase the generalization error in semi-supervised learning. This study proposes a novel framework for semi-supervised learning termed consistency-regularized bad generative adversarial network (CRBSGAN) through a new loss function. The proposed model comprises a discriminator, a bad generator, and a classifier that employs data augmentation and consistency regularization. Local augmentation is created to compensate for data scarcity and boost bad generators. Moreover, label consistency regularization is considered for bad fake images, real labeled images, unlabeled images, and latent space for the discriminator and bad generator. In the adversarial game between the discriminator and the bad generator, feature space is better captured under these conditions. Furthermore, local consistency regularization for good-augmented images applied to the classifier strengthens the bad generator in the generator-classifier adversarial game. The consistency-regularized bad generator produces informative fake images similar to the support vectors located near the correct classification boundary. In addition, the pseudo-label error is reduced for low-confidence unlabeled images used in training. The proposed method reduces the state-of-the-art error rate from 6.44 to 4.02 on CIFAR-10, 2.06 to 1.56 on MNIST, and 6.07 to 3.26 on SVHN using 4000, 3000, and 500 labeled training images, respectively. Furthermore, it achieves a reduction in the error rate on the CINIC-10 dataset from 19.38 to 15.32 and on the STL-10 dataset from 27 to 16.34 when utilizing 1000 and 500 labeled images per class, respectively. Experimental results and visual synthesis indicate that the CRBSGAN algorithm is more efficient than the methods proposed in previous works. The source code is available at https://github.com/ms-iraji/CRBSGAN ↗.

##The key contributions of our work are as follows:

1- We propose a novel framework that employs local consistency regularization to labeled, unlabeled, and latent data in three-player bad generative semi-supervised networks to improve their performance.

2- A novel type of consistency regularization loss, termed local consistency regularization for bad fake images, is introduced. The consistent bad generator efficiently learns the feature space and generates more accurate bad images (i.e., more informative images) near the true decision boundary through local consistency regularization applied to the latent space of bad fake images.

3- The local consistency regularization for good-augmented images with reliable labels applied to the classifier in the proposed framework, better adjusts the margin of the classifier for pseudo labels generated from fake images. This action strengthens the bad generator in the generator-classifier adversarial game.

4- We demonstrate that the applied consistency regularization improves the proposed bad generative semi-supervised model, reducing the consistency-regularized semi-supervised classifier error. Reducing incorrect pseudo-labels for unlabeled images, particularly for images below the class threshold probability, lessens model error and strengthens the generalization performance of the classifier.

5- We provide a theoretical analysis of empirical risk for bad semi-supervised generative adversarial networks. 

6- We demonstrate that a transformer-based discriminator provides a better signal to the bad generator in three-player bad semi-supervised generative adversarial networks.

## Key Features
- Visual data analysis
- Consistency regularization for bad fake images
- Local consistency regularization for good-augmented images
- Improved semi-supervised classification performance
- Reduction in pseudo-label errors for low-confidence images
- Theoretical analysis of empirical risk for bad semi-supervised generative adversarial networks

## Installation and Usage

To use the CRBSGAN algorithm, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Configure the training parameters and dataset paths in the provided configuration file.
4. Run `main-stl.ipynb` from STL-10 folder in colab.


## Results

The CRBSGAN algorithm has been evaluated on several benchmark datasets, including  MNIST, CIFAR-10, and SVHN. The experimental results demonstrate its effectiveness in reducing error rates compared to state-of-the-art methods. For detailed results, please refer to the [Results](#results) section in the paper.


## Contributing

Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please submit a pull request or open an issue on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
