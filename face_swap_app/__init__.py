import logging
import os


logs_path = os.path.join(os.getcwd(),'face_swap_app','artifacts', 'logs')
logging.basicConfig(filename=os.path.join(logs_path, "app.logs"),
                    format='[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
