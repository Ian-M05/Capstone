from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db_conn
from app import schemas
from app.security import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserOut, status_code=201)
def signup(payload: schemas.SignupRequest, conn=Depends(get_db_conn)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM users WHERE username=%s OR email=%s LIMIT 1",
            (payload.username.strip().lower(), payload.email.lower()),
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="User with that username/email already exists")

        password_val = hash_password(payload.password)
        cur.execute(
            """
            INSERT INTO users (first_name, last_name, email, username, password_hash)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, first_name, last_name, email, username
            """,
            (
                payload.first_name.strip(),
                payload.last_name.strip(),
                payload.email.lower(),
                payload.username.strip().lower(),
                password_val,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "username": row[4],
        }


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, conn=Depends(get_db_conn)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username=%s",
            (payload.username.strip().lower(),),
        )
        row = cur.fetchone()
        if not row or not verify_password(payload.password, row[1]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(subject=str(row[0]))
        return schemas.TokenResponse(access_token=token)


@router.get("/validate")
def validate(token: str):
    claims = decode_token(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"valid": True, "claims": claims}
