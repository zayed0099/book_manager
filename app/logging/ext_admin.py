import logging
# from app.resources.admin import Admin_Crud, Admin_Book_Manage, User_Control, Jwt_Manage

logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info('Started')

    admin_crud = Admin_Crud()
    admin_crud.get()
    admin_crud.post()
    admin_crud.put()
    admin_crud.delete()

    admin_book_manage = Admin_Book_Manage()
    admin_book_manage.get()

    user_control = User_Control()
    user_control.put()
    user_control.delete()

    jwt = Jwt_Manage()
    jwt.delete()
    
    logger.info('Finished')

if __name__ == '__main__':
    main()
