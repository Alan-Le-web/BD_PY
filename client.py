import psycopg2

def create_db(conn):
    with conn.cursor() as cur:

        cur.execute("""
        DROP TABLE PhoneBook;
        DROP TABLE Clients;
        """)           

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Clients(
        ClientID SERIAL PRIMARY KEY,
        Firstname VARCHAR(18) NOT NULL,
        Lastname VARCHAR(30) NOT NULL,
        Email VARCHAR(40) UNIQUE NOT NULL            
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook(
            PhoneID SERIAL PRIMARY KEY,
            ClientID INTEGER REFERENCES Clients(ClientID),
            PhoneNumber VARCHAR(15) UNIQUE 
        );
        """)
        conn.commit()
    

def add_client(conn, FirstName, LastName, Email, PhoneNumber=None ):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO Clients (Firstname, Lastname, Email) 
        VALUES (%s, %s, %s);
        """, (FirstName, LastName, Email))
        cur.execute("SELECT ClientID FROM Clients WHERE Email = %s;", (Email,)) # сверяем по email
        ClientID = cur.fetchone()[0] # присваеваем индекс ID
        
        if PhoneNumber: # если номер указан то записываем его в таблицу
            for phone in PhoneNumber:
                cur.execute(""" 
                INSERT INTO PhoneBook (ClientID, PhoneNumber) 
                VALUES (%s, %s);
                """, (ClientID, phone))
    conn.commit() 

def add_phone(conn, ClientID, PhoneNumber):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO PhoneBook (ClientID, PhoneNumber) 
        VALUES (%s, %s);
        """, (ClientID, PhoneNumber))    
        conn.commit() 
    
def change_client(conn, ClientID, FirstName=None, LastName=None, Email=None, PhoneNumber=None):
    with conn.cursor() as cur:
        
        if FirstName is not None:
            cur.execute("""
                UPDATE Clients SET Firstname=%s WHERE ClientID=%s
                """, (FirstName, ClientID)) 
       
        if LastName is not None:
            cur.execute("""
                UPDATE Clients SET Lastname=%s WHERE ClientID=%s
                """, (LastName, ClientID)) 
        
        if Email is not None:
            cur.execute("""
                UPDATE Clients SET Email=%s WHERE ClientID=%s
                """, (Email, ClientID)) 
       
        if PhoneNumber is not None:
            # Преобразовываем телефоны в список, если это не список
            if not isinstance(PhoneNumber, list):
                PhoneNumber = [PhoneNumber]
            
            # Удаляем старые телефоны
            cur.execute("DELETE FROM PhoneBook WHERE ClientID=%s;", (ClientID,))
            
            # Добавляем новые
            for phone in PhoneNumber:
                cur.execute("""
                    INSERT INTO PhoneBook (ClientID, PhoneNumber) 
                    VALUES (%s, %s);
                    """, (ClientID, phone))
    
    conn.commit()

def delete_phone(conn, ClientID, PhoneNumber):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM PhoneBook WHERE ClientID = %s AND PhoneNumber = %s; 
            """, (ClientID, PhoneNumber))    
    conn.commit() 

def delete_client(conn, ClientID):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM PhoneBook WHERE ClientID = %s; 
            """, (ClientID, ))    
    conn.commit()


def find_client(conn, FirstName=None, LastName=None, Email=None, PhoneNumber=None):
    with conn.cursor() as cur:
        query = "SELECT * FROM Clients c JOIN PhoneBook p ON c.ClientID = p.ClientID WHERE"
        conditions = []
        params = []

        if FirstName is not None:
            conditions.append("c.FirstName = %s")
            params.append(FirstName)
        
        if LastName is not None:
            conditions.append("c.LastName = %s")
            params.append(LastName)
        
        if Email is not None:
            conditions.append("c.Email = %s")
            params.append(Email)

        if PhoneNumber is not None:
            conditions.append("p.PhoneNumber = %s")
            params.append(PhoneNumber)

        # Если не указаны фильтры, вернуть все клиенты
        if not conditions:
            query = "SELECT * FROM Clients c JOIN PhoneBook p ON c.ClientID = p.ClientID"
        else:
            query += " " + " AND ".join(conditions)

        cur.execute(query, tuple(params))
        results = cur.fetchall()
        print(results)        
       


            
       

with psycopg2.connect(database='bd_py_connect', user='postgres', password='ufo') as conn:
    create_db(conn)
    add_client(conn, 'Сергей', 'Петров', 'petrov@mail.ru', [333, 444])
    add_client(conn, 'Eva', 'Sanders', 'sanders@gmail.com', [555, 666])
    add_phone(conn, 1, '23423423')
    add_phone(conn, 1, '123423423')
    delete_phone (conn, 1, '23423423')
    change_client(conn, 1,'John',None,'dsf@dfsg.com')
    find_client(conn, 'John')
conn.close()