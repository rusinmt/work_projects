## OpenCV Table Anonymization

Facing a menial and time-consuming task of anonymizing a large number of rows for over 1500 court cases, I developed a solution incorporating OpenCV on the pictures/scans prepared for the job to automate and speed up the process.

The idea behind this project is to detect structures of a table, then find corners where row and column contours intersect. These corner points will act as references to connect them by a bounding line, detecting each individual row on an image or scanned document that may be skewed, rotated, and of low quality.

The pipeline for detecting the table structure in the image starts by converting the input image, from a PDF page, to grayscale. I decided to use [Adaptive Gaussian Thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) to avoid set interval for threshold values due to the varying image quality and wide range of different pictures taken in different light conditions. Horizontal and vertical kernels and morphological opening indicate the structures that are then filtered to yield the best effect for this case scenario. The filter is used to bring out the main table structure, further exposing the desired area of the image.
```python
kernel = np.ones((5,5), np.uint8)
dilated = cv2.dilate(filtered_lines, kernel, iterations=2)
contours, * = cv2.findContours(dilated, cv2.RETR*EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_structure_mask = np.zeros_like(filtered_lines)
if contours:
    main_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(main_structure_mask, [main_contour], -1, 255, thickness=cv2.FILLED)
```
This code identifies and isolates the space of the table sheet. By dilating the lines, it connects nearby elements, making it easier to identify the overall structure. Lines that are too short, like artifacts from stamps, are removed for a clearer reading of the table structure.
On an image made of horizontal and vertical lines that were vividly extrapolated in the last step, the code adapts the [Harris Corner Detection](https://docs.opencv.org/4.x/dc/d0d/tutorial_py_features_harris.html) algorithm to identify intersections of said lines. CCentered points are used as references to locate row contours and define the boundaries of the table area.

Diving deeper into the solution, vertical contours are sorted to establish a reliable column order by assigning corner points to columns based on their proximity to vertical lines. The added 'min_distance' parameter ensures that points that are too close to each other are not indexed. Paths connecting borders of indexed corner points create boundaries for rows. These paths are used in masking, creating separate masks for the whole table (excluding the first row of indexed corners to make the header visible) and individual rows.
```python
def create_row_images(image, paths):
    row_images = []
    height, width = image.shape[:2]
   
    table_mask = np.zeros((height, width), dtype=np.uint8)
    for i in range(len(paths) - 1):
        cv2.fillPoly(table_mask, [np.array(paths[i] + paths[i+1][::-1], dtype=np.int32)], 255)
   
    for i in range(len(paths) - 1):
        im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        row_image = im.copy()
       
        current_row_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(current_row_mask, [np.array(paths[i] + paths[i+1][::-1], dtype=np.int32)], 255)
        inverted_current_row_mask = cv2.bitwise_not(current_row_mask)
        final_mask = cv2.bitwise_and(table_mask, inverted_current_row_mask)
        white_overlay = np.full(image.shape, 255, dtype=np.uint8)
        row_image = np.where(final_mask[:, :, None] == 255, white_overlay, row_image)
        row_images.append(row_image)
    return row_images
```
The code processes pages in the PDF document, saving each page in a separate folder that contains all detected rows enumerated in order. These rows were renamed using Excel files provided by the client to make the retrieval of desired data more efficient.


### Showcase

Example of two random table sheets from a quick image search, using const=500 to include smaller perimeters of contours in a table mask.

<img src="https://github.com/user-attachments/assets/b584d909-79a2-4d58-8de9-f384fc349532" width="32%"> <img src="https://github.com/user-attachments/assets/76ae53dc-722c-494f-9277-27f37be51cca" width="32%"> <img src="https://github.com/user-attachments/assets/1a0ef521-c330-4f18-9527-344a2f8fc51e" width="32%">

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Corners* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Indexed Corners* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Pathing*

### Results
<img src="https://github.com/user-attachments/assets/8ac90bbb-472f-4561-b813-da44305390b5" width="47%"> <img src="https://github.com/user-attachments/assets/311c51f9-eb38-4dcc-876f-dc5a6c7aad06" width="47%">

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Row 3* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Row 2*
