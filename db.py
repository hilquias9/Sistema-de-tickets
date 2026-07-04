import psycopg2
import bcrypt
from auth import DB_CONNECTION
from fastapi import HTTPException



class User:
    @staticmethod
    def login(email,password):
        with psycopg2.connect(DB_CONNECTION) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT id,password_hash,role FROM users WHERE email=%s""",(email,))
                member=cursor.fetchone()
                if member is None:
                    raise HTTPException(status_code=401,detail="INVALID EMAIL OR PASSWORD")
                if not bcrypt.checkpw(password.encode(),hashed_password=member[1].encode()):
                    raise HTTPException(status_code=401,detail="INVALID EMAIL OR PASSWORD")
                return [member[0],member[2]]
    


class TeamMember:
    @staticmethod
    def new_member(name,email,password):
        try:
            password_hash=bcrypt.hashpw(password=password.encode(),salt=bcrypt.gensalt()).decode()
            role="team_member"
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""INSERT INTO users(name,email,password_hash,role) VALUES (%s,%s,%s,%s)""",(name,email,password_hash,role,))
        except psycopg2.errors.UniqueViolation:
            raise HTTPException(status_code=409, detail="THIS EMAIL ADDRESS IS ALREADY IN USE")
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO new_member ",error)
            raise HTTPException(status_code=500,detail="DB ERROR")

    @staticmethod
    def member_info(id:int):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""SELECT name,email FROM users WHERE id=%s AND role=%s""",(id,"team_member"))
                    member=cursor.fetchone()
                    dictionary={"id":id,
                                "name":member[0],
                                "email":member[1]
                                }
                    return dictionary
        except psycopg2.Error:
            raise HTTPException(status_code=500,detail="MEMBER INFO ERROR")

    @staticmethod
    def member_off(id:int):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""UPDATE users SET active=%s WHERE id=%s """,(False,id,))
        except Exception as error:
            print("NÃO FOI POSSÍVEL DESLIGAR O TEAM_MEMBER, ",error)

    @staticmethod
    def member_on(id:int):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""UPDATE users SET active=%s WHERE id=%s """,(True,id,))
        except Exception as error:
            print("NÃO FOI POSSÍVEL LIGAR O TEAM_MEMBER, ",error)

class Client:

    @staticmethod
    def new_client(name,email,phone_number:str | None,password):
        role="client"
        password_hash=bcrypt.hashpw(password.encode(),salt=bcrypt.gensalt()).decode()
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""INSERT INTO users(name,email,password_hash,phone_number,role) VALUES (%s,%s,%s,%s,%s)""",(name,email,password_hash,phone_number,role,))
        except psycopg2.errors.UniqueViolation:
            raise HTTPException(status_code=409, detail="THIS EMAIL ADDRESS IS ALREADY IN USE")
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO new_client ",error)
            raise HTTPException(status_code=500,detail="DB ERROR")

    @staticmethod
    def client_info(id:int):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""SELECT name,email FROM users WHERE id=%s AND role=%s""",(id,"client"))
                    member=cursor.fetchone()
                    titles=Tickets.see_client_open_tickets(id)
                    dictionary={"id":id,
                                "name":member[0],
                                "email":member[1],
                                "tickets_title":titles
                                }
                    return dictionary
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO client_info ",error)
            raise HTTPException(status_code=500,detail="MEMBER INFO ERROR")

class Tickets:
    @staticmethod
    def new_ticket(title,msg,id):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""INSERT INTO tickets(client_id,title,description) VALUES (%s,%s,%s)""",(id,title,msg))
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO new_ticket ",error)
            raise HTTPException(status_code=500,detail="DB_ERROR")
    
    @staticmethod
    def see_client_open_tickets(id):
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""SELECT title FROM tickets WHERE client_id=%s and status=%s""",(id,"open",))
                    titles_list=[]
                    titles=cursor.fetchall()
                    for title in titles:
                        titles_list.append(title[0])
                    return titles_list
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO see_client_open_tickets ",error)
            raise HTTPException(status_code=500,detail="SEEOPENTICKETS")
    
    @staticmethod
    def see_all_open_tickets():
        try:
            with psycopg2.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""SELECT tickets.client_id,users.name,tickets.title,tickets.description,tickets.created_at 
                                   FROM tickets JOIN users ON tickets.client_id = users.id WHERE tickets.status=%s""",("open",))
                    tickets_pulled=cursor.fetchall()
                    if len(tickets_pulled)>0:
                        tickets_dict={}
                        counter=0
                        for ticket in tickets_pulled:
                            created_at=str(ticket[4])
                            tickets_dict[counter]={"id":[ticket[0],ticket[1]],"title":ticket[2],"description":ticket[3],
                                                "created_at":f"{created_at[:10]}"
                                                }
                            counter+=1
                        return tickets_dict
        except psycopg2.Error as error:
            print("OCORREU UM ERRO AO USAR A FUNÇÃO see_all_open_tickets ",error)
            raise HTTPException(status_code=500,detail="PULLTICKETS")

