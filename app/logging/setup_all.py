import logging


# --- Admin logger 
admin_logger = logging.getLogger("myapp.admin")
admin_handler = logging.FileHandler("logs/admin.log")
admin_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

admin_handler.setFormatter(admin_formatter)
admin_logger.addHandler(admin_handler)
admin_logger.setLevel(logging.INFO)
admin_logger.propagate = False   # don't send messages up to root

# --- Werkzeug logger
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_handler = logging.FileHandler("logs/werkzeug.log")
werkzeug_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

werkzeug_handler.setFormatter(werkzeug_formatter)
werkzeug_logger.addHandler(werkzeug_handler)
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.propagate = False  # same


# --- SQLAlchemy logger ---
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_handler = logging.FileHandler("logs/sqlalchemy.log")
sqlalchemy_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

sqlalchemy_handler.setFormatter(sqlalchemy_formatter)
sqlalchemy_logger.addHandler(sqlalchemy_handler)
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.propagate = False


def main():
    admin_logger.info("Started admin actions")

    admin_crud = Admin_Crud()
    admin_crud.get()
    admin_crud.post()
    
    admin_ud = AdminUD()
    admin_ud.put()
    admin_ud.delete()

    admin_book_manage = Admin_Book_Manage()
    admin_book_manage.get()

    user_control = User_Control()
    user_control.put()
    user_control.delete()

    jwt = Jwt_Manage()
    jwt.delete()

    uad = UserAccDelete()
    uad.delete()

    us = UserStat()
    us.get()

    bm = BookManage()
    bm.delete()

    ucc = UserCredChange()
    ucc.post()

    ush = User_Show()
    ush.get()

    admin_logger.info("Finished admin actions")


if __name__ == '__main__':
    main()
