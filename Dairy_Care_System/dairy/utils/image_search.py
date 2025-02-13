from google.cloud import vision
import numpy as np
import cv2
from ..models import Products_table, ProductImage
from django.db.models import Q

class ImageSearcher:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        
    def get_image_labels(self, image_bytes):
        """Get labels from Google Vision API"""
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.label_detection(image=image)
            return [label.description.lower() for label in response.label_annotations]
        except Exception as e:
            print(f"Error getting labels: {str(e)}")
            return []

    def get_image_text(self, image_bytes):
        """Get text from image using OCR"""
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.text_detection(image=image)
            if response.text_annotations:
                return response.text_annotations[0].description.lower().split()
            return []
        except Exception as e:
            print(f"Error getting text: {str(e)}")
            return []

    def search_products(self, image_file):
        """Search for products based on image content"""
        try:
            # Read image bytes
            image_bytes = image_file.read()
            
            # Get labels and text from image
            labels = self.get_image_labels(image_bytes)
            text_in_image = self.get_image_text(image_bytes)
            
            # Combine all detected terms
            all_terms = set(labels + text_in_image)
            
            # Define relevant categories and terms
            dairy_terms = {
                'milk', 'dairy', 'cheese', 'yogurt', 'butter', 'cream', 
                'curd', 'ghee', 'paneer', 'buttermilk', 'food', 'drink',
                'bottle', 'container', 'product', 'package'
            }
            
            # Check if any relevant terms are found
            matching_terms = all_terms.intersection(dairy_terms)
            
            if not matching_terms:
                # If no dairy-related terms found, try visual similarity
                return self.find_visually_similar_products(image_bytes)
            
            # Search for products matching the detected terms
            query = Q()
            for term in matching_terms:
                query |= (
                    Q(product_name__icontains=term) |
                    Q(product_description__icontains=term) |
                    Q(product_category__icontains=term)
                )
            
            products = Products_table.objects.filter(query).distinct()
            
            if not products.exists():
                # If no products found by terms, try visual similarity
                return self.find_visually_similar_products(image_bytes)
            
            return next(iter(matching_terms)), list(products)
            
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return None, []

    def find_visually_similar_products(self, image_bytes):
        """Find visually similar products"""
        try:
            # Convert uploaded image to OpenCV format
            nparr = np.frombuffer(image_bytes, np.uint8)
            uploaded_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if uploaded_img is None:
                return None, []
            
            # Resize for consistent comparison
            uploaded_img = cv2.resize(uploaded_img, (224, 224))
            uploaded_hist = cv2.calcHist([uploaded_img], [0, 1, 2], None, [8, 8, 8], 
                                       [0, 256, 0, 256, 0, 256])
            cv2.normalize(uploaded_hist, uploaded_hist)
            
            similar_products = []
            for product in Products_table.objects.all():
                for image in product.images.all():
                    try:
                        # Read and process product image
                        product_img = cv2.imread(image.image.path)
                        if product_img is None:
                            continue
                            
                        product_img = cv2.resize(product_img, (224, 224))
                        product_hist = cv2.calcHist([product_img], [0, 1, 2], None, 
                                                  [8, 8, 8], [0, 256, 0, 256, 0, 256])
                        cv2.normalize(product_hist, product_hist)
                        
                        # Compare histograms
                        similarity = cv2.compareHist(uploaded_hist, product_hist, 
                                                   cv2.HISTCMP_CORREL)
                        
                        # If similarity is high enough, consider it a match
                        if similarity > 0.5:  # Adjust this threshold as needed
                            similar_products.append(product)
                            break  # Move to next product once a match is found
                            
                    except Exception as e:
                        print(f"Error comparing images: {str(e)}")
                        continue
            
            if similar_products:
                return "visually similar", similar_products
                
            return None, []
            
        except Exception as e:
            print(f"Error in visual search: {str(e)}")
            return None, []