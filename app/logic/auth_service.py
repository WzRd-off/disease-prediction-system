class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager

    def authenticate(self, login, password):
        """
        Проверяет логин и пароль.
        Возвращает данные пользователя (dict) если успешно, иначе None.
        """
        
        query = "SELECT * FROM users WHERE login = ? AND password = ?"
        user = self.db.execute_query(query, (login, password), fetch_one=True)
        
        if user:
            return dict(user) # Превращаем sqlite3.Row в обычный словарь
        
        return None