import cv2
from IPython.display import Video
import matplotlib.pyplot as plt
import numpy as np
import math
#%matplotlib inline  

def run(back,frt): #frt:视频
    
    back_crop = back[1200:3700,0:2160]

    desired_height = 1500
    desired_width = int((back_crop.shape[1]/back_crop.shape[0]) * desired_height)
    dim = ((desired_width),(desired_height)) #int
    back_shrink = cv2.resize(back_crop,dsize=dim,interpolation=cv2.INTER_AREA)

    color_range = {'green':[(0, 120, 0),(130,255,130)]} 
    detect_color = 'green'
    back_mask = cv2.inRange(back_shrink,color_range[detect_color][0],color_range[detect_color][1])
    opened = cv2.morphologyEx(back_mask,cv2.MORPH_OPEN,np.ones((6,6),np.uint8)) #去白点
    closed = cv2.morphologyEx(opened,cv2.MORPH_CLOSE,np.ones((6,6),np.uint8)) #去黑点
    
    contours = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    areaMaxContour, contourAreaMax = getAreaMaxContour(contours)
    minAreaRect = cv2.minAreaRect(areaMaxContour)
    box = np.int0(cv2.boxPoints(minAreaRect))
    w = np.max(minAreaRect[1])
    h = np.min(minAreaRect[1])
    new_size = np.int0(np.ceil([w,h])) #minAreaRect returns 90 degree rotated (w,h)
    frt_resize = cv2.resize(frt,new_size) #order: w,h

    baseplate = np.zeros(back_shrink.shape, np.uint8)
    centre = minAreaRect[0] #(x,y)
    y_min = round(centre[1]-h/2)
    y_max = round(centre[1]+h/2)
    x_min = round(centre[0]-w/2)
    x_max = round(centre[0]+w/2)
    baseplate[y_min:y_max,x_min:x_max] = frt_resize[0:y_max-y_min,0:x_max-x_min]
    

    if 80<minAreaRect[2]<90:
     M = cv2.getRotationMatrix2D(centre, (90-minAreaRect[2]), 1.0)
    elif minAreaRect[2]>90:
     M = cv2.getRotationMatrix2D(centre, -(minAreaRect[2]-90), 1.0)
    elif minAreaRect[2]==90:
     M = cv2.getRotationMatrix2D(centre, 0, 1.0)s
    elif minAreaRect[2]==0:
     M = cv2.getRotationMatrix2D(centre, 0, 1.0)
    #elif 0<minAreaRect[2]<10:
    else:
     M = cv2.getRotationMatrix2D(centre, -minAreaRect[2], 1.0)
  
    
    rotated = cv2.warpAffine(baseplate, M, dim)
    mask_rotated = cv2.bitwise_and(rotated,rotated,mask=closed)
    
    back_inv = cv2.bitwise_not(closed)
    background = cv2.bitwise_and(back_shrink, back_shrink, mask=back_inv)
    result = cv2.add(mask_rotated,background)
    
    return result

def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓
  
    
cap_back = cv2.VideoCapture('computer.mp4')
cap_frt = cv2.VideoCapture('play.mp4')
out_avi = cv2.VideoWriter('out9.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 25, (1296,1500))
        
for i in range(344):
    ret1,back = cap_back.read()
    ret2,frt = cap_frt.read()
    if ret1 and ret2 ==True:
        result = run(back,frt)
        out_avi.write(result)
        
cap_back.release()
cap_frt.release()
out_avi.release()
        