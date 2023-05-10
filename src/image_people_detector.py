from typing import List
import cv2
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image
import torch


def get_people_coords(path: str, debug=False) -> List[List[int]]:

  image = Image.open(path)
  image_cv2 = cv2.imread(path)

  model = YolosForObjectDetection.from_pretrained('hustvl/yolos-tiny')
  processor = YolosImageProcessor.from_pretrained("hustvl/yolos-tiny")

  text_queries = [
      ["human face", "person"],
  ]
  images = [image] # todo: check more than one frame
  inputs = processor(text=text_queries, images=images, return_tensors="pt")
  outputs = model(**inputs)

  target_sizes = [torch.tensor(image.size[::-1])]
  results= processor.post_process_object_detection(outputs, threshold=0.90, target_sizes=target_sizes)[0]

  ppl = []
  for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    lb = [int(round(i,1)) for i in box.tolist()]
    x, y, x2, y2 = tuple(lb)
    ppl.append([x, y, x2, y2])
    cv2.rectangle(image_cv2, (x,y), (x2,y2), (0, 0, 255), 2)
    print(f"{model.config.id2label[label.item()]} {round(score.item(), 3)} at location {lb}")

  if debug:
    cv2.imshow("", image_cv2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  return ppl
