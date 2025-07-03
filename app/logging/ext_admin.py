# myapp.py
import logging
from app.resources.admin import Admin_Crud, Admin_Book_Manage, User_Control

logger = logging.getLogger(__name__)
    
def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')
    Admin_Crud.get()
    Admin_Crud.post()
    Admin_Crud.put()
    Admin_Crud.delete()
    Admin_Book_Manage.get()
    User_Control.put()
    User_Control.delete()

    logger.info('Finished')

if __name__ == '__main__':
    main()