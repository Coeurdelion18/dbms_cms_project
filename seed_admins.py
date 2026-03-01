from db_backend.auth_ops import create_user

admins = [

("admin1@cms.com","Admin One","admin123"),

("admin2@cms.com","Admin Two","admin123"),


]

for email,name,pw in admins:

    print(create_user(email,name,pw,"admin"))