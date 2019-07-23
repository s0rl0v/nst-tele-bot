# Description

AWS-based solution of Neural Style Transfer app.

## Technologies

* AWS Lambda/Python=3.7 with python-telegram-bot to orchestrate all of this
* S3 to store data/MQ
* S3 triggers to notify Lambda on new images in S3
* AWS Batch on GPU(P-series EC2 instances) to run style transfer

# How to build and deploy

## Prerequisites

* AWS account
* `awscli`
* `sam`

## Steps

1. Clone this repo and cd to it;
2. Build lambda package:
```
# sam build --use-container -t cloudformation\template.yaml -s .
```
3. Upload the package to s3:
```
# sam package --s3-bucket okeer-dev --output-template-file package.yaml
```
4. Deploy the stack to AWS:
*NOTE*: do not forget to replace `telegram_bot_api_key` and `any_available_name` with actual values.

```
# aws cloudformation deploy --template-file package.yaml --stack-name nst --capabilities CAPABILITY_IAM --force-upload --parameter-overrides "ApiKey=`telegram_bot_api_key`" "BucketName=`any_available_name`"
```
5. Download [VGG19](http://www.vlfeat.org/matconvnet/models/imagenet-vgg-verydeep-19.mat) model to `any_available_name` S3 bucket along with style.jpg image - this image style will be used in image processing;
6. Post an image to telegram bot and wait until app will process it.

# Reference

*deeplearning.ai for implementation of NST model.*

The Neural Style Transfer algorithm was due to Gatys et al. (2015). Harish Narayanan and Github user "log0" also have highly readable write-ups from which we drew inspiration. The pre-trained network used in this implementation is a VGG network, which is due to Simonyan and Zisserman (2015). Pre-trained weights were from the work of the MathConvNet team.

* [Leon A. Gatys, Alexander S. Ecker, Matthias Bethge, (2015). A Neural Algorithm of Artistic Style](https://arxiv.org/abs/1508.06576)
* [Harish Narayanan, Convolutional neural networks for artistic style transfer.](https://harishnarayanan.org/writing/artistic-style-transfer/)
* [Log0, TensorFlow Implementation of "A Neural Algorithm of Artistic Style".](http://www.chioka.in/tensorflow-implementation-neural-algorithm-of-artistic-style)
* [Karen Simonyan and Andrew Zisserman (2015). Very deep convolutional networks for large-scale image recognition] (https://arxiv.org/pdf/1409.1556.pdf)
* [MatConvNet](http://www.vlfeat.org/matconvnet/pretrained/)
