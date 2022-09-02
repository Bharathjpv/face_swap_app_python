import dlib
import cv2
import numpy as np
import logging
import os
import logging
from face_swap_app.utils import index_nparray, transformation, save_img

logger = logging.getLogger(__name__)

class face_app():
    def __init__(self, source_filepath, destination_filepath):
        try:
            self.source_filepath = source_filepath
            self.destination_filepath = destination_filepath
            self.points_detector = None
            logger.info('face_app instance created')
        except Exception as e:
            logger.error(e)
            raise e
    
    def read_destination_image(self):
        try:
            self.img = cv2.imread(self.destination_filepath)
            self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            self.mask = np.zeros_like(self.img_gray)
            self.face_detector = dlib.get_frontal_face_detector()
            self.points_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            self.faces = self.face_detector(self.img_gray)
            logger.info('Destination Image read')
        except Exception as e:
            logger.error(e)
            raise e
        
    def create_contour(self):
        try:
            for face in self.faces:
                self.points = self.points_detector(self.img_gray, face)
                self.points_list = []
                for n in range(0, 68):
                    x = self.points.part(n).x
                    y = self.points.part(n).y
                    self.points_list+=[(x, y)]

                self.points = np.array(self.points_list, np.int32)
                self.convexhull = cv2.convexHull(self.points)
                cv2.fillConvexPoly(self.mask, self.convexhull, 255)
                self.face_image_1 = cv2.bitwise_and(self.img, self.img, mask=self.mask)
            logger.info('Contour Created')
        except Exception as e:
            logging.error(e)
            raise e
    
    def extract_triangles(self):
        try:
            rect = cv2.boundingRect(self.convexhull)
            subdiv = cv2.Subdiv2D(rect)
            subdiv.insert(self.points_list)
            triangles = subdiv.getTriangleList()
            self.triangles = np.array(triangles, dtype=np.int32)
        except Exception as e:
            logger.error(e)
            raise e
        
    def create_triangle_id(self):
        try:
            self.triangles_id = []

            for t in self.triangles:
                pt1 = (t[0], t[1])
                pt2 = (t[2], t[3])
                pt3 = (t[4], t[5])

                id_pt1 = np.where((self.points == pt1).all(axis=1))
                id_pt1 = index_nparray(id_pt1)
                id_pt2 = np.where((self.points == pt2).all(axis=1))
                id_pt2 = index_nparray(id_pt2)
                id_pt3 = np.where((self.points == pt3).all(axis=1))
                id_pt3 = index_nparray(id_pt3)

                if id_pt1 is not None and id_pt2 is not None and id_pt3 is not None:
                    triangle = [id_pt1, id_pt2, id_pt3]
                    self.triangles_id.append(triangle)
            logger.info('triangle id created')
        except Exception as e:
            logger.error(e)
            raise e
    
    def read_source_image(self):
        try:
            self.img2 = cv2.imread(self.source_filepath)

            self.img2_gray = cv2.cvtColor(self.img2, cv2.COLOR_BGR2GRAY)

            faces2 = self.face_detector(self.img2_gray)
            logger.info('Extraction of source image pints started')
            for face in faces2:
                points_predict2 = self.points_detector(self.img2_gray, face)
                self.points_list2 = []
                for n in range(0, 68):
                    x = points_predict2.part(n).x
                    y = points_predict2.part(n).y
                    self.points_list2.append((x, y))
                points2 = np.array(self.points_list2, np.int32)
                self.convexhull2 = cv2.convexHull(points2)
            logger.info('Extraction finished')
        except Exception as e:
            logger.error(e)
            raise e
        
    def fit(self):
        try:
            logger.info('Face mask creating started')
            self.img2_new_face = np.zeros_like(self.img2, np.uint8)
            for triangle_index in self.triangles_id:
            
                cropped_triangle, points, cropped_tr1_mask, rect1 = transformation(triangle_index, self.img, self.points_list)


                cropped_triangle2, points2, cropped_tr2_mask, rect2 = transformation(triangle_index, self.img2, self.points_list2)

                (x2, y2, w2, h2) = rect2

                points = np.float32(points)
                points2 = np.float32(points2)
                M = cv2.getAffineTransform(points, points2)
                warped_triangle = cv2.warpAffine(cropped_triangle, M, (w2, h2))
                warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=cropped_tr2_mask)


                img2_new_face_rect_area = self.img2_new_face[y2: y2 + h2, x2: x2 + w2]
                img2_new_face_rect_area_gray = cv2.cvtColor(img2_new_face_rect_area, cv2.COLOR_BGR2GRAY)
                
                _, mask_triangles_designed = cv2.threshold(img2_new_face_rect_area_gray, 1, 255, cv2.THRESH_BINARY_INV)
                warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=mask_triangles_designed)

                img2_new_face_rect_area = cv2.add(img2_new_face_rect_area, warped_triangle)
                self.img2_new_face[y2: y2 + h2, x2: x2 + w2] = img2_new_face_rect_area
            logger.info('Face Mask Created')
        except Exception as e:
            logger.error(e)
            raise e
    
    def render_face(self):
        try:
            logger.info('Rendering generated image')
            img2_face_mask = np.zeros_like(self.img2_gray)
            img2_head_mask = cv2.fillConvexPoly(img2_face_mask, self.convexhull2, 255)
            img2_face_mask = cv2.bitwise_not(img2_head_mask)
            img2_noface = cv2.bitwise_and(self.img2, self.img2, mask=img2_face_mask)


            result = cv2.add(img2_noface, self.img2_new_face)

            #cloning face into the img2
            (x3, y3, w3, h3) = cv2.boundingRect(self.convexhull2)
            center_face = (int((x3 + x3 + w3) / 2), int((y3 + y3 + h3) / 2))
            self.seamlessclone = cv2.seamlessClone(result, self.img2, img2_head_mask, center_face, cv2.MONOCHROME_TRANSFER)

            save_img(os.path.join(os.getcwd(), 'static/images/modified.jpg'), self.seamlessclone)
            # cv2.imwrite('image.jpg', self.seamlessclone)
            logger.info('rendering finished')
        except Exception as e:
            logger.error(e)
            raise e
    
    def run(self):
        self.read_destination_image()
        self.create_contour()
        self.extract_triangles()
        self.create_triangle_id()
        self.read_source_image()
        self.fit()
        self.render_face()