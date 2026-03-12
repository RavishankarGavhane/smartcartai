from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "user": current_user}
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "user": current_user}
    )

@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "orders.html", 
        {"request": request, "user": current_user}
    )

@router.get("/orders/{order_number}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request,
    order_number: str,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "order_detail.html", 
        {"request": request, "user": current_user, "order_number": order_number}
    )

@router.get("/cart", response_class=HTMLResponse)
async def cart_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "cart.html", 
        {"request": request, "user": current_user}
    )

@router.get("/product/{product_id}", response_class=HTMLResponse)
async def product_page(
    request: Request,
    product_id: int,
    current_user = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        "product.html", 
        {"request": request, "user": current_user, "product_id": product_id}
    )

@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "checkout.html", 
        {"request": request, "user": current_user}
    )

@router.get("/deals", response_class=HTMLResponse)
async def deals_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        "deals.html", 
        {"request": request, "user": current_user}
    )



@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    """Render forgot password page"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    token: str,
    current_user = Depends(get_current_user_from_cookie)
):
    """Render reset password page with token"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "reset_password.html", 
        {"request": request, "token": token}
    )


@router.get("/reset-password-confirmation", response_class=HTMLResponse)
async def reset_password_confirmation_page(
    request: Request,
    current_user = Depends(get_current_user_from_cookie)
):
    """Render password reset confirmation page"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "reset_password_confirmation.html", 
        {"request": request}
    )