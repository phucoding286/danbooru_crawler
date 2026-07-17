import cv2, os, random

image = cv2.imread("./danbooru_images_crawled" + "/" + random.choice(os.listdir("./danbooru_images_crawled")))
print(image.shape)
cv2.imshow("Danbooru Image", image)
cv2.waitKey(0)