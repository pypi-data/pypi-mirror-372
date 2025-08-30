import cv2
import numpy as np
def removeSmallPatches(binary_mask, min_pixels=50, min_area=40, 
                                 circularity_threshold=0.1):
    binary_mask = (binary_mask > 0).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary_mask, connectivity=8
    )    
    output_mask = np.zeros_like(binary_mask)    
    for i in range(1, num_labels):
        pixel_count = stats[i, cv2.CC_STAT_AREA]        
        if pixel_count < min_pixels:
            continue
        component_mask = (labels == i).astype(np.uint8)
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)        
        if contours:
            contour = contours[0]
            area = cv2.contourArea(contour)            
            if area < min_area:
                continue                
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity < circularity_threshold:
                    continue        
        output_mask[labels == i] = 255    
    return output_mask

"""
mask = removeSmallPatches(b, min_pixels=50, min_area=40, 
                                 circularity_threshold=0.1)
data = np.where(mask, data, 0)

filtered_data = np.full([256,256],0)
filtered_data[mask] = e[mask]
"""