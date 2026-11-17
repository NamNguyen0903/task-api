def register(username, password):
    if not username or len(password) < 8:
        return "Registration failed"
    return "Registration successful"
