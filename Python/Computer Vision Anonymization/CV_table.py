# ROWER

import os
import cv2
from PIL import Image
import numpy as np
from pdf2image import convert_from_path

def process_pdf_page(image, page_number, output_folder):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Automated Thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Extract Horizontal Lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find Contours for Horizontal Lines
    contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    const = 1200
    
    # Create Mask for Horizontal Contours Longer than 'const'
    mask_horizontal = np.zeros_like(horizontal_lines)
    for contour in contours:
        if cv2.arcLength(contour, True) > const:
            cv2.drawContours(mask_horizontal, [contour], -1, 255, thickness=cv2.FILLED)
    
    # Apply Mask to Detected Horizontal Lines
    filtered_horizontal_lines = cv2.bitwise_and(horizontal_lines, horizontal_lines, mask=mask_horizontal)
    
    # Extract Vertical Lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find Contours for Vertical Lines
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create Mask for Vertical Contours Longer than 'const'
    mask_vertical = np.zeros_like(vertical_lines)
    for contour in contours:
        if cv2.arcLength(contour, True) > const:
            cv2.drawContours(mask_vertical, [contour], -1, 255, thickness=cv2.FILLED)
    
    # Apply Mask to Detected Vertical Lines
    filtered_vertical_lines = cv2.bitwise_and(vertical_lines, vertical_lines, mask=mask_vertical)
    
    # Combine Filtered Horizontal and Vertical Lines
    filtered_lines = cv2.add(filtered_horizontal_lines, filtered_vertical_lines)
    
    # Create a mask for the main table structure
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(filtered_lines, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_structure_mask = np.zeros_like(filtered_lines)
    if contours:
        main_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(main_structure_mask, [main_contour], -1, 255, thickness=cv2.FILLED)
    
    final_result = cv2.bitwise_and(filtered_lines, filtered_lines, mask=main_structure_mask)
    
    # Detect Corners using Harris Corner Detection
    corners = cv2.cornerHarris(final_result, 3, 5, 0.12)
    corners = cv2.dilate(corners, None)
    
    # Convert the Harris response to a binary image
    _, corners_binary = cv2.threshold(corners, 0.01 * corners.max(), 255, 0)
    corners_binary = np.uint8(corners_binary)
    
    # Find centroids of the corners
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(corners_binary)
    
    # Extract corner points
    corner_points = []
    for i in range(1, len(centroids)):
        x, y = centroids[i]
        corner_points.append((int(x), int(y)))
        
    indexed_corners = index_corners(corner_points, filtered_vertical_lines, filtered_horizontal_lines)
    complete_paths = crumb(indexed_corners)
    row_images = create_row_images(image, complete_paths)
    save_images_as_pdfs(row_images, os.path.join(output_folder, f"page_{page_number}"))

def index_corners(corner_points, vertical_lines, horizontal_lines, tolerance=10, min_distance=15):
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours from left to right
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    
    indexed_corners = []
    for col, contour in enumerate(contours, start=1):
        # Get all points from the contour
        contour_points = contour.reshape(-1, 2)
        
        column_corners = []
        for point in corner_points:
            distances = np.abs(contour_points[:, 0] - point[0])
            if distances.min() < tolerance:
                column_corners.append(point)
        
        # Sort corners by y-coordinate
        column_corners.sort(key=lambda p: p[1])
        
        # Filter out points that are too close to each other
        filtered_corners = []
        if column_corners:
            filtered_corners.append(column_corners[0])
            for i in range(1, len(column_corners)):
                if abs(column_corners[i][1] - filtered_corners[-1][1]) >= min_distance:
                    filtered_corners.append(column_corners[i])
        
        # Add indexed corners
        for row, point in enumerate(filtered_corners[1:]):
            indexed_corners.append((point, (col, row)))
    
    return indexed_corners

def crumb(indexed_corners):
    rows_dict = {}
    for point, (col, row) in indexed_corners:
        if row not in rows_dict:
            rows_dict[row] = []
        rows_dict[row].append((col, point))
    
    paths = []
    for row, points in sorted(rows_dict.items()):
        points = sorted(points, key=lambda x: x[0])
        paths.append([p[1] for p in points])  
    return paths

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

def save_images_as_pdfs(images, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for i, img in enumerate(images):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        pdf_path = os.path.join(output_folder, f"row_{i+1}.pdf")
        img_pil.save(pdf_path, "PDF", resolution=100.0, save_all=True)

pdf_path = r"C:\Users\Mateusz\Desktop\nordecum_actl.pdf"
images = convert_from_path(pdf_path)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_folder = os.path.join(desktop_path, "cover")
os.makedirs(output_folder, exist_ok=True)

for page_num, image in enumerate(images, start=1):
    image_np = np.array(image)
    process_pdf_page(image_np, page_num, output_folder)
