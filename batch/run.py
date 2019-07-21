# NST code from (C) deeplearning.ai

import os

from datetime import datetime
from utils.misc import *
from utils.graph import TFGraph

CONTENT_IMAGE = f'content.{os.environ["SESSION_ID"]}.jpg'
STYLE_IMAGE = 'style.jpg'
GENERATED_IMAGE = f'generated.{os.environ["SESSION_ID"]}.jpg'

MODEL_FILE = "imagenet-vgg-verydeep-19.mat"

step = datetime.now()

graph = TFGraph(CONTENT_IMAGE, STYLE_IMAGE, MODEL_FILE)
generated_image = graph.run(300)

# save last generated image
save_image(GENERATED_IMAGE, generated_image)

print("Saved generated image")
print(f'Elapsed time {datetime.now() - step}')
