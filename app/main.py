from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.models import User
from app.auth.database import session_factory

# Создаем приложение
app = FastAPI()

# Подключение статики
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="app/templates")

# Конфигурация безопасности
SECRET_KEY = "your_secret_key"  # Замените на свой секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Задаем схему авторизации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функция для создания хэша пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для генерации JWT токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register")
async def register_user(user: str = Form(...), password: str = Form(...)):
    # Серверная валидация длины
    if len(user) < 5 or len(password) < 5:
        raise HTTPException(status_code=400, detail="Username and password must be at least 5 characters long")

    # Проверка на существование пользователя с таким же именем
    with session_factory() as session:
        existing_user = session.query(User).filter(User.username == user).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Сохранение нового пользователя
        hashed_password = get_password_hash(password)
        new_user = User(username=user, password=hashed_password)
        session.add(new_user)
        session.commit()

    # Перенаправление после успешной регистрации
    return RedirectResponse(url="/", status_code=303)

# Маршрут для получения токена (вход)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with session_factory() as session:
        user = session.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

# Защищенный маршрут для приветствия
@app.get("/welcome", response_class=HTMLResponse)
async def read_welcome(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return HTMLResponse(content=f"""
    <html>
    <head>
        <style>
            body {{
                background-color: #808080; /* Светлый фон */
                color: #808080; /* Темный цвет текста */
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: 'Open Sans', 'sans-serif';
            }}
            h1 {{
                font-size: 36px; /* Увеличенный размер шрифта */
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>Добро пожаловать, {username}!</h1>
    </body>
    </html>
    """, status_code=200)




