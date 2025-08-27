mlclassifier is a package with custom algorithms to classify data using ml. It currently only supports image classification.

To install it, use ```pip install mlclassifier```.

To classify images, you must have a dataset for the images with this folder structure

```
dataset_folder/
├── class1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── class2/
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

The image names or class names don't matter. The classifier assigns a class number in the order of classes from top to bottom.

To classify images, you first need to train the model using ```ImageClassifierTrainer```.

```python
from mlclassifier import ImageClassifierTrainer # import the trainer
import mlclassifier # import the package

trainer = ImageClassifierTrainer("<the_path_to_your_dataset", method=mlclassifier.PICK_BEST,  # Create the ImageClassiferTrainerObject
                                 resize_size=(128, 128), model_path="<path_you_want_to_save_the_model>",
                                 n_runs=5) 

trainer.fit() # train the model
```

The ```method``` parameter is used to specify which feature extraction method to use. 
You can use HOG (```mlclassifier.HOG```), or ORB (```mlclassifier.ORB```), or LBP (```mlclassifier.LBP```), or you can make it run all 3 and save the best one using ```mlclassifier.PICK_BEST```.

The ```resize_size``` parameter is the size you want to resize all the images to for consistency

The ```n_runs``` parameter is used to set the number of times you want to train the classifier. It will pick the best trained one out of all the runs and save it.

The model_path parameter must be a .pkl file.

At the end of the training cycle, it will print the Average FPS if you were to stream images to it, the time it took per image, and the score.

After training, you can start classifying images using ```ImageClassifier```.

```python
from mlclassifier import ImageClassifier # import the ImageClassifier 
import cv2 # import cv2

classifier = ImageClassifier("<model_path>") # create the classifier object
image = cv2.imread("<path_to_your_image") # read the image

predicted_class = classifier.predict(image) # predict the class

print(predicted_class) # print the predicted class
```
