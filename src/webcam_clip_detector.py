import cv2
import numpy as np


def find_webcam_clip2(image_path):
    # Read the image and convert to grayscale
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 20, 50)

    # Apply morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # Filter contours based on size and aspect ratio
    webcam_clip_contour = None
    contours_filtered = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        webcam_clip_contour = contour
        contours_filtered.append(contour)

    # Draw the bounding box around the detected contour
    x, y, w, h = cv2.boundingRect(webcam_clip_contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.drawContours(image, contours_filtered, -1, (0, 255, 0), 2)

    # Show the image with the bounding box
    # cv2.imshow("Detected Edges", edges)
    cv2.imshow("Detected Webcam Clip", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Return the position and size of the webcam clip
    return x, y, w, h

def find_webcam_clip(image_path, threshold=30, distance_tolerance=20):
    # Read the image and convert to grayscale
    image = cv2.imread(image_path)
    preview_image = image.copy()
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    _, thresh = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours_filtered = []
    distance_tolerance = 20
    for contour in contours:
      x, y, w, h = cv2.boundingRect(contour)
      if (x <= distance_tolerance or y <= distance_tolerance or
        x + w >= image.shape[1] - distance_tolerance or
        y + h >= image.shape[0] - distance_tolerance):
        contours_filtered.append(contour)

    cv2.drawContours(preview_image, contours_filtered, -1, (0, 255, 0), 2)


    # # Detect lines using HoughLinesP
    # lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    # preview_image = image.copy()

    # # Find the bounding box around the detected lines
    # x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0
    # for line in lines:
    #     x1, y1, x2, y2 = line[0]

    #     # Skip lines around the entire screen
    #     if (x1 > distance_tolerance and x2 > distance_tolerance and
    #         y1 > distance_tolerance and y2 > distance_tolerance and
    #         x1 < image.shape[1] - distance_tolerance and x2 < image.shape[1] - distance_tolerance and
    #         y1 < image.shape[0] - distance_tolerance and y2 < image.shape[0] - distance_tolerance):

    #         x_min, y_min = min(x_min, x1, x2), min(y_min, y1, y2)
    #         x_max, y_max = max(x_max, x1, x2), max(y_max, y1, y2)
    #         cv2.line(preview_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Draw the bounding box on the copied image

    # cv2.rectangle(preview_image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)



    # Find the contour that is close to the corners or touching the screen boundaries, has a minimum size, and has straight lines
    # max_area = 0
    # webcam_clip_contour = None
    # distance_tolerance = 20
    # min_width = 100
    # min_height = 100
    # boundary_tolerance = 2
    # approximation_precision = 0.02

    # print(f"found countrous - ", len(contours))
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     x, y, w, h = cv2.boundingRect(contour)
    #     if w < min_width or h < min_height:
    #         continue

    #     print('passed size ration', x,y,w,h)

    #     if area > max_area and (x <= distance_tolerance or y <= distance_tolerance or
    #                             x + w >= image.shape[1] - distance_tolerance or
    #                             y + h >= image.shape[0] - distance_tolerance):
    #       # Ignore contour around the entire screen
    #       if x > boundary_tolerance and y > boundary_tolerance and x + w < image.shape[1] - boundary_tolerance and y + h < image.shape[0] - boundary_tolerance:
    #           # Approximate contour and check if it has four vertices (rectangular shape)
    #           epsilon = approximation_precision * cv2.arcLength(contour, True)
    #           approx = cv2.approxPolyDP(contour, epsilon, True)

    #           if len(approx) == 4:
    #               max_area = area
    #               webcam_clip_contour = contour



    # # Find the bounding box of the largest contour
    # x, y, w, h = cv2.boundingRect(webcam_clip_contour)

    # # Draw the bounding box on the copied image
    # cv2.rectangle(image_with_contours, (x, y), (x + w, y + h), (0, 0, 255), 3)

    # Show the copied image with contours and bounding box
    # cv2.imshow("Detected Contours and Bounding Box", image_with_contours)

    cv2.imshow("preview image", preview_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Return the position and size of the webcam clip
    return x, y, w, h

# Example usage
image_path = '/Users/kk/projects/twitch_clips2yt_shorts_automation/temp/test.jpg'
# x, y, w, h = find_webcam_clip(image_path, 40)
x, y, w, h = find_webcam_clip2(image_path)

print(f'Webcam clip position: ({y}, {x}), height: {h}, width: {w}')
