# NST code from (C) deeplearning.ai

from datetime import datetime
from utils.misc import *
from utils.graph import TFGraph

CONTENT_IMAGE = 'input/content.jpg'
STYLE_IMAGE = 'input/style.jpg'
GENERATED_IMAGE = 'output/generated.jpg'

MODEL_FILE = "C:/Users/Okeer/conv/week4/Neural Style Transfer/pretrained-model/imagenet-vgg-verydeep-19.mat" #"imagenet-vgg-verydeep-19.mat"

step = datetime.now()

graph = TFGraph(CONTENT_IMAGE, STYLE_IMAGE, MODEL_FILE)
generated_image = graph.run(1)

# save last generated image
save_image(GENERATED_IMAGE, generated_image)

print("Saved generated image")
print(f'Elapsed time {datetime.now() - step}')
