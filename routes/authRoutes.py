from tasks.tasks import send_email_report_dashboard
from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.models import User
from app.auth.database import session_factory
from app.auth.config import settings

router = APIRouter()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register_user(user: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if len(user) < 5 or len(password) < 5:
        raise HTTPException(status_code=400, detail="Username and password must be at least 5 characters long")

    with session_factory() as session:
        existing_user = session.query(User).filter(User.username == user).first()
        existing_email = session.query(User).filter(User.email == email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = get_password_hash(password)
        new_user = User(username=user, email=email, password=hashed_password)
        session.add(new_user)
        session.commit()

        # Отправка приветственного письма
        send_email_report_dashboard.delay(user, email)

    return RedirectResponse(url="/", status_code=303)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with session_factory() as session:
        user = session.query(User).filter(User.email == form_data.username).first()

        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "email": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/welcome", response_class=HTMLResponse)
async def read_welcome(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        email: str = payload.get("email")
        if username is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return HTMLResponse(content=f"""
    <html>
    <head>
        <style>
            body {{
                background-color: #808080;
                color: #808080;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: 'Open Sans', 'sans-serif';
            }}
            h1 {{
                font-size: 36px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>Добро пожаловать, {username}!</h1>
    </body>
    </html>
    """, status_code=200)


