from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from openai import project
from .models import *
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages




from django.db.models import Sum
from .models import Client, Project, Payment, Spend


from django.db.models import Sum
from decimal import Decimal


from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from .models import Client, Project, Payment, Spend



from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages



import os
from datetime import datetime
from django.conf import settings

def cleanup_old_backups(days=30):
    """
    Auto delete backup files older than given days.
    Safe for production.
    """
    backup_dir = os.path.join(settings.BASE_DIR, "backups")

    if not os.path.exists(backup_dir):
        return

    now_ts = datetime.now().timestamp()

    for filename in os.listdir(backup_dir):
        if not filename.lower().endswith(".zip"):
            continue

        file_path = os.path.join(backup_dir, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            file_age_days = (now_ts - os.path.getctime(file_path)) / 86400

            if file_age_days > days:
                os.remove(file_path)
        except Exception:
            # don't crash backup if delete fails
            pass




def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'billing/auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')





from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal
from datetime import datetime


from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime

@login_required(login_url='login')
def dashboard(request):

    # =====================================
    # TOTALS
    # =====================================
    total_clients = Client.objects.count()
    total_projects = Project.objects.count()

    total_payments = (
        Payment.objects.aggregate(total=Sum('amount'))['total']
        or Decimal("0.00")
    )

    total_spend = (
        Spend.objects.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('qty') * F('rate'),
                    output_field=DecimalField()
                )
            )
        )['total']
        or Decimal("0.00")
    )

    # =====================================
    # PROJECT MATRIX
    # =====================================
    projects_queryset = (
        Project.objects
        .select_related('client')
        .annotate(
            paid_amount=Coalesce(Sum('payments__amount'), Decimal("0.00"))
        )
    )

    projects = []

    for project in projects_queryset:
        budget = project.budget or Decimal("0.00")
        paid = project.paid_amount or Decimal("0.00")

        progress = 0
        if budget > 0:
            progress = int((paid / budget) * 100)

        # ✅ STATUS COLOR MAPPING
        status_color_map = {
            "completed": "success",
            "ongoing": "warning",
            "hold": "secondary",
        }

        projects.append({
            "id": project.id,
            "name": project.name,
            "client_name": project.client.name,
            "budget": budget,
            "paid": paid,
            "remaining": budget - paid,
            "progress": min(progress, 100),

            # 🔥 NEW
            "status": project.status,  # raw value
            "status_display": project.get_status_display(),  # readable
            "status_color": status_color_map.get(project.status, "dark"),
        })

    # =====================================
    # RECENT ACTIVITY
    # =====================================
    payments = Payment.objects.select_related(
        'project__client'
    ).order_by('-date')[:5]

    spends = Spend.objects.select_related(
        'project'
    ).order_by('-created_at')[:5]

    activities = []

    for p in payments:
        dt = datetime.combine(p.date, datetime.min.time())
        dt = timezone.make_aware(dt)

        activities.append({
            "type": "payment",
            "date": dt,
            "title": "Payment Received",
            "description": f"{p.project.client.name} paid for {p.project.name}",
            "amount": p.amount,
            "color": "success",
        })

    for s in spends:
        activities.append({
            "type": "spend",
            "date": s.created_at,
            "title": "Expense Logged",
            "description": f"{s.project.name} expense entry",
            "amount": s.total_amount,
            "color": "danger",
        })

    activities = sorted(
        activities,
        key=lambda x: x["date"],
        reverse=True
    )[:5]

    # =====================================
    # CONTEXT
    # =====================================
    context = {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_payments": total_payments,
        "total_spend": total_spend,
        "projects": projects,
        "activities": activities,
    }

    return render(request, "billing/dashboard.html", context)




###########################################

# client login/logout and dashboard views


import re

def get_client_password(client):

    name = client.name.lower().strip()

    name = re.sub(
        r'^(mr|mrs|ms|miss)\.?\s*',
        '',
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(r'[^a-z0-9]', '', name)

    return f"{name}{client.mobile_1[-4:]}"


from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from .models import Client


@require_http_methods(["GET", "POST"])
def client_login(request):

    if request.session.get("client_id"):
        return redirect("client_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        client = Client.objects.filter(
            mobile_1=username
        ).first()

        if not client:
            messages.error(request, "Mobile number not registered")
            return render(
                request,
                "billing/client_auth/login.html"
            )

        # Password = client name + last 4 digits
        expected_password = get_client_password(client)

        if password.lower() == expected_password.lower():

            request.session["client_id"] = client.id

            return redirect("client_dashboard")

        messages.error(request, "Invalid password")

    return render(
        request,
        "billing/client_auth/login.html"
    )




def client_logout(request):
    request.session.pop("client_id", None)
    return redirect("login")


# from django.shortcuts import get_object_or_404, render, redirect
# from django.db.models import Sum
# from decimal import Decimal

# def client_dashboard(request):

#     client_id = request.session.get("client_id")

#     if not client_id:
#         return redirect("client_login")

#     client = get_object_or_404(Client, id=client_id)

#     projects = Project.objects.filter(client=client)

#     latest_project = projects.order_by('-id').first()
#     project_status = latest_project.status if latest_project else None

#     # ✅ CORRECT
#     completed_projects = projects.filter(status="Completed").exists()

#     payments = (
#         Payment.objects
#         .filter(project__client=client)
#         .select_related("project")
#         .order_by("-date")
#     )

#     total_paid = payments.aggregate(
#         total=Sum("amount")
#     )["total"] or Decimal("0.00")

#     total_budget = projects.aggregate(
#         total=Sum("budget")
#     )["total"] or Decimal("0.00")

#     total_receivable = total_budget - total_paid

#     return render(request, "billing/client_auth/dashboard.html", {
#         "client": client,
#         "projects": projects,
#         "payments": payments,
#         "total_paid": total_paid,
#         "total_budget": total_budget,
#         "total_receivable": total_receivable,
#         "project_status": project_status,
#         "has_completed_projects": completed_projects,
#     })



from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Sum
from decimal import Decimal
from datetime import date, timedelta

def client_dashboard(request):
    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    client = get_object_or_404(Client, id=client_id)
    projects = Project.objects.filter(client=client)
    latest_project = projects.order_by('-id').first()
    project_status = latest_project.status if latest_project else None

    completed_projects = projects.filter(status="completed").exists()

    payments = (
        Payment.objects
        .filter(project__client=client)
        .select_related("project")
        .order_by("-date")
    )

    total_paid = payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    total_budget = projects.aggregate(total=Sum("budget"))["total"] or Decimal("0.00")
    total_receivable = total_budget - total_paid

    # ═══════════════════════════════════════════
    #  PROJECT MILESTONES & TIMELINE
    # ═══════════════════════════════════════════
    enriched_projects = []
    
    for project in projects:
        # Calculate payment percentage
        if project.budget > 0:
            payment_progress = float((project.total_paid / project.budget) * 100)
        else:
            payment_progress = 0

        # Define milestones based on status
        if project.status == "completed":
            milestones = [
                {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                {"name": "Design Approval", "status": "completed", "icon": "bi-pencil-square"},
                {"name": "Material Selection", "status": "completed", "icon": "bi-palette-fill"},
                {"name": "Production Completed", "status": "completed", "icon": "bi-hammer"},
                {"name": "Installation Done", "status": "completed", "icon": "bi-tools"},
                {"name": "Final Handover", "status": "completed", "icon": "bi-house-check-fill"},
            ]
        elif project.status == "ongoing":
            # Dynamic milestones based on payment progress
            if payment_progress < 20:
                milestones = [
                    {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                    {"name": "Site Measurement", "status": "ongoing", "icon": "bi-rulers"},
                    {"name": "Design Approval", "status": "pending", "icon": "bi-pencil-square"},
                    {"name": "Material Selection", "status": "pending", "icon": "bi-palette-fill"},
                    {"name": "Production Started", "status": "pending", "icon": "bi-hammer"},
                    {"name": "Installation", "status": "pending", "icon": "bi-tools"},
                    {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
                ]
            elif payment_progress < 40:
                milestones = [
                    {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                    {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                    {"name": "Design Approval", "status": "ongoing", "icon": "bi-pencil-square"},
                    {"name": "Material Selection", "status": "pending", "icon": "bi-palette-fill"},
                    {"name": "Production Started", "status": "pending", "icon": "bi-hammer"},
                    {"name": "Installation", "status": "pending", "icon": "bi-tools"},
                    {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
                ]
            elif payment_progress < 60:
                milestones = [
                    {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                    {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                    {"name": "Design Approval", "status": "completed", "icon": "bi-pencil-square"},
                    {"name": "Material Selection", "status": "ongoing", "icon": "bi-palette-fill"},
                    {"name": "Production Started", "status": "pending", "icon": "bi-hammer"},
                    {"name": "Installation", "status": "pending", "icon": "bi-tools"},
                    {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
                ]
            elif payment_progress < 80:
                milestones = [
                    {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                    {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                    {"name": "Design Approval", "status": "completed", "icon": "bi-pencil-square"},
                    {"name": "Material Selection", "status": "completed", "icon": "bi-palette-fill"},
                    {"name": "Production Started", "status": "ongoing", "icon": "bi-hammer"},
                    {"name": "Installation", "status": "pending", "icon": "bi-tools"},
                    {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
                ]
            else:
                milestones = [
                    {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                    {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                    {"name": "Design Approval", "status": "completed", "icon": "bi-pencil-square"},
                    {"name": "Material Selection", "status": "completed", "icon": "bi-palette-fill"},
                    {"name": "Production Started", "status": "completed", "icon": "bi-hammer"},
                    {"name": "Installation", "status": "ongoing", "icon": "bi-tools"},
                    {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
                ]
        else:  # on_hold
            milestones = [
                {"name": "Initial Consultation", "status": "completed", "icon": "bi-chat-dots-fill"},
                {"name": "Site Measurement", "status": "completed", "icon": "bi-rulers"},
                {"name": "Design Approval", "status": "hold", "icon": "bi-pencil-square"},
                {"name": "Material Selection", "status": "pending", "icon": "bi-palette-fill"},
                {"name": "Production Started", "status": "pending", "icon": "bi-hammer"},
                {"name": "Installation", "status": "pending", "icon": "bi-tools"},
                {"name": "Final Handover", "status": "pending", "icon": "bi-house-check-fill"},
            ]

        # ═══════════════════════════════════════════
        #  PROJECT HEALTH SCORE
        # ═══════════════════════════════════════════
        project_health = {
            "status": "on_track",
            "label": "On Track",
            "color": "success",
            "icon": "bi-check-circle-fill",
            "reasons": []
        }

        # Check payment health
        if payment_progress < 30 and project.status == "ongoing":
            project_health = {
                "status": "critical",
                "label": "Critical",
                "color": "danger",
                "icon": "bi-exclamation-triangle-fill",
                "reasons": ["Low payment progress", "Project may stall"]
            }
        elif payment_progress < 50 and project.status == "ongoing":
            project_health = {
                "status": "attention",
                "label": "Attention Needed",
                "color": "warning",
                "icon": "bi-exclamation-circle-fill",
                "reasons": ["Payment pending", "Material procurement delayed"]
            }
        elif project.status == "hold":
            project_health = {
                "status": "attention",
                "label": "On Hold",
                "color": "secondary",
                "icon": "bi-pause-circle-fill",
                "reasons": ["Project paused", "Awaiting approval"]
            }
        else:
            project_health["reasons"] = [
                "Payments on schedule",
                "Timeline healthy",
                "Work progressing"
            ]

        # ═══════════════════════════════════════════
        #  PROJECT COUNTDOWN (Expected handover)
        # ═══════════════════════════════════════════
        # Calculate expected handover (estimate: 90 days from creation for ongoing)
        if project.status == "ongoing":
            expected_handover = project.created_at.date() + timedelta(days=90)
            days_remaining = (expected_handover - date.today()).days
            
            if days_remaining < 0:
                countdown = {
                    "date": expected_handover,
                    "days": abs(days_remaining),
                    "status": "overdue",
                    "label": f"{abs(days_remaining)} days overdue"
                }
            else:
                countdown = {
                    "date": expected_handover,
                    "days": days_remaining,
                    "status": "active",
                    "label": f"{days_remaining} days remaining"
                }
        elif project.status == "completed":
            # Use last payment date as handover date
            last_payment = payments.filter(project=project).order_by('-date').first()
            handover_date = last_payment.date if last_payment else project.created_at.date()
            countdown = {
                "date": handover_date,
                "days": 0,
                "status": "completed",
                "label": "Project Delivered"
            }
        else:
            countdown = {
                "date": None,
                "days": 0,
                "status": "pending",
                "label": "Timeline pending"
            }

        enriched_projects.append({
            "project": project,
            "milestones": milestones,
            "payment_progress": round(payment_progress, 1),
            "health": project_health,
            "countdown": countdown,
        })

    return render(request, "billing/client_auth/dashboard.html", {
        "client": client,
        "projects": enriched_projects,
        "payments": payments,
        "total_paid": total_paid,
        "total_budget": total_budget,
        "total_receivable": total_receivable,
        "project_status": project_status,
        "has_completed_projects": completed_projects,
    })




from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

def client_invoice_view(request, token):

    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    payment = get_object_or_404(
        Payment.objects.select_related("project__client"),
        invoice_token=token
    )

    # 🔒 SECURITY — client can only see their invoice
    if payment.project.client_id != client_id:
        messages.error(request, "Unauthorized access")
        return redirect("client_dashboard")

    context = build_invoice_context(request, payment)
    context["is_public"] = True  # important

    return render(
        request,
        "billing/client_auth/invoice_view.html",
        context
    )



from django.db.models import Q

# 📌 List
def client_list(request):

    query = request.GET.get('q')

    clients = Client.objects.all().order_by('-id')

    if query:
        clients = clients.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile_1__icontains=query) |
            Q(mobile_2__icontains=query)
        )

    context = {
        'clients': clients,
        'query': query
    }

    return render(request, 'billing/client/index.html', context)



# 📌 Create
def client_create(request):
    if request.method == 'POST':
        Client.objects.create(
            name=request.POST.get('name'),
            mobile_1=request.POST.get('mobile_1'),
            mobile_2=request.POST.get('mobile_2'),
            address=request.POST.get('address'),
            email=request.POST.get('email'),
            notes=request.POST.get('notes'),
            gst_number=request.POST.get('gst_number'),
            discount=request.POST.get('discount') or 0,
        )
        return redirect('client_list')

    return render(request, 'billing/client/create.html')


# 📌 Update
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client.name = request.POST.get('name')
        client.mobile_1 = request.POST.get('mobile_1')
        client.mobile_2 = request.POST.get('mobile_2')
        client.address = request.POST.get('address')
        client.email = request.POST.get('email')
        client.notes = request.POST.get('notes')
        client.gst_number = request.POST.get('gst_number')
        client.discount = request.POST.get('discount') or 0
        client.save()

        return redirect('client_list')

    return render(request, 'billing/client/update.html', {'client': client})

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from .models import Client, Project, Payment, Spend
from decimal import Decimal

def client_detail(request, pk):
    """
    Client detail view showing all client information,
    associated projects, payments, and financial summary.
    """
    client = get_object_or_404(Client, pk=pk)
    
    # Get all projects for this client
    projects = Project.objects.filter(client=client).order_by('-created_at')
    
    # Calculate project statistics
    project_stats = []
    total_budget = Decimal('0')
    total_spent = Decimal('0')
    total_paid = Decimal('0')
    
    for project in projects:
        # Calculate spent for this project
        # Option 1: If total_amount is a property, calculate manually
        spends = Spend.objects.filter(project=project)
        
        # Calculate total - adjust based on your model structure
        # If total is qty * rate:
        spent = spends.aggregate(
            total=Sum(F('qty') * F('rate'), output_field=DecimalField())
        )['total'] or Decimal('0')
        
        # OR if total is area * rate:
        # spent = spends.aggregate(
        #     total=Sum(F('area') * F('rate'), output_field=DecimalField())
        # )['total'] or Decimal('0')
        
        # OR if you have a property method, loop through:
        # spent = sum(Decimal(str(s.total_amount)) for s in spends)
        
        # Calculate paid for this project
        paid = Payment.objects.filter(project=project).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Balance for this project
        balance = spent - paid
        
        # Progress percentage
        if project.budget and project.budget > 0:
            progress = min(int((spent / project.budget) * 100), 100)
        else:
            progress = 0
        
        project_stats.append({
            'project': project,
            'spent': spent,
            'paid': paid,
            'balance': balance,
            'progress': progress,
        })
        
        total_budget += project.budget or Decimal('0')
        total_spent += spent
        total_paid += paid
    
    total_balance = total_spent - total_paid
    
    # Get recent payments across all client's projects
    recent_payments = Payment.objects.filter(
        project__client=client
    ).select_related('project').order_by('-date', '-id')[:10]
    
    # Payment rows with running balance calculation
    payment_rows = []
    for payment in recent_payments:
        payment_rows.append({
            'id': payment.id,
            'date': payment.date.strftime('%d %b %Y') if payment.date else '-',
            'project': payment.project.name,
            'project_id': payment.project.id,
            'amount': payment.amount,
            'mode': getattr(payment, 'mode', None) or 'Cash',
            'whatsapp_url': generate_whatsapp_url(client, payment),
        })
    
    # Project count by status
    status_counts = {
        'ongoing': projects.filter(status='ongoing').count(),
        'completed': projects.filter(status='completed').count(),
        'hold': projects.filter(status='hold').count(),
    }
    
    context = {
        'client': client,
        'projects': projects,
        'project_stats': project_stats,
        'recent_payments': payment_rows,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_paid': total_paid,
        'total_balance': total_balance,
        'status_counts': status_counts,
        'project_count': projects.count(),
        'payment_count': Payment.objects.filter(project__client=client).count(),
    }
    
    return render(request, 'billing/client/client_detail.html', context)


def generate_whatsapp_url(client, payment):
    """Generate WhatsApp share URL for payment receipt"""
    phone = client.mobile_1 or ''
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, str(phone)))
    
    message = f"""🏠 *HomeDen Payment Receipt*

Dear {client.name},

Thank you for your payment!

📋 *Project:* {payment.project.name}
💰 *Amount:* ₹{payment.amount:,.2f}
📅 *Date:* {payment.date.strftime('%d %b %Y') if payment.date else '-'}

Thank you for your trust in HomeDen!
"""
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/91{phone}?text={encoded_message}"





# 📌 Delete
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client.delete()
        return redirect('client_list')

    return render(request, 'billing/client/delete.html', {'client': client})



# 📌 Project List
# def project_list(request):

#     query = request.GET.get('q')

#     projects = Project.objects.select_related('client').order_by('-id')

#     # 🔍 Apply filter
#     if query:
#         projects = projects.filter(
#             Q(name__icontains=query) |
#             Q(client__name__icontains=query)
#         )

#     # 🔥 Calculate total receivable AFTER filtering
#     total_receivable = Decimal("0.00")
#     for project in projects:
#         total_receivable += project.yet_to_receive

#     context = {
#         'projects': projects,
#         'total_receivable': total_receivable,
#         'query': query,
#     }

#     return render(request, 'billing/project/index.html', context)



# views.py

from datetime import date
from decimal import Decimal
from django.db.models import Sum, Min, Max
from django.shortcuts import render


def project_list(request):

    projects = Project.objects.select_related('client').all().order_by('-id').annotate(
        first_payment_date=Min('payments__date'),
        last_payment_date=Max('payments__date'),
        annotated_total_paid=Sum('payments__amount'),
    )

    today = date.today()

    project_list_qs = list(projects)

    for project in project_list_qs:

        # ═══════════════════════════════════
        #  PROJECT START DATE
        # ═══════════════════════════════════
        if project.created_at:
            created_date = project.created_at.date()
            project.start_date = created_date
            project.age_days = (today - created_date).days
        else:
            project.start_date = None
            project.age_days = 0

        # ═══════════════════════════════════
        #  PAYMENT TIMELINE
        # ═══════════════════════════════════
        if project.first_payment_date:
            delta = today - project.first_payment_date
            project.days_elapsed = delta.days

            if project.last_payment_date:
                last_delta = today - project.last_payment_date
                project.last_activity_days = last_delta.days
            else:
                project.last_activity_days = None

            days = delta.days
            if days == 0:
                project.duration_label = "Today"
            elif days == 1:
                project.duration_label = "1 day"
            elif days < 7:
                project.duration_label = f"{days} days"
            elif days < 30:
                weeks = days // 7
                project.duration_label = f"{weeks} week{'s' if weeks > 1 else ''}"
            elif days < 365:
                months = days // 30
                extra_days = days % 30
                if extra_days > 0:
                    project.duration_label = f"{months}m {extra_days}d"
                else:
                    project.duration_label = f"{months} month{'s' if months > 1 else ''}"
            else:
                years = days // 365
                months = (days % 365) // 30
                project.duration_label = f"{years}y {months}m"

            if days <= 30:
                project.duration_status = "fresh"
            elif days <= 90:
                project.duration_status = "active"
            elif days <= 180:
                project.duration_status = "aging"
            else:
                project.duration_status = "old"

        else:
            project.days_elapsed = None
            project.last_activity_days = None
            project.duration_label = "Not started"
            project.duration_status = "none"

        # ═══════════════════════════════════
        #  PENDING AMOUNT & PAYMENT STATUS
        # ═══════════════════════════════════
        paid = project.annotated_total_paid or Decimal("0.00")
        raw_pending = project.budget - paid
        project.pending_amount = raw_pending if raw_pending > 0 else Decimal("0.00")

        if project.pending_amount <= 0:
            project.payment_status = "paid"
        elif project.last_activity_days is not None and project.last_activity_days <= 15:
            project.payment_status = "healthy"
        elif project.last_activity_days is not None and project.last_activity_days <= 30:
            project.payment_status = "warning"
        else:
            project.payment_status = "danger"

        # ═══════════════════════════════════
        #  SHOW NO-PAYMENT ALERT (> 30 days)
        # ═══════════════════════════════════
        if not project.first_payment_date and project.age_days > 30:
            project.show_payment_alert = True
        elif project.last_activity_days is not None and project.last_activity_days > 30:
            project.show_payment_alert = True
        else:
            project.show_payment_alert = False

    # ═══════════════════════════════════
    #  TOTAL RECEIVABLE STAT
    # ═══════════════════════════════════
    total_receivable = sum(
        p.pending_amount
        for p in project_list_qs
        if p.pending_amount > 0
    )
    count = len(project_list_qs)

    return render(request, 'billing/project/index.html', {
        'projects': project_list_qs,
        'total_receivable': total_receivable,
        'count': count,
        'today': today,
    })



# 📌 Project Create
def project_create(request):
    clients = Client.objects.all()

    if request.method == 'POST':
        Project.objects.create(
            client_id=request.POST.get('client'),
            name=request.POST.get('name'),
            budget=request.POST.get('budget') or 0,
            status=request.POST.get('status'),
        )
        return redirect('project_list')

    return render(request, 'billing/project/create.html', {'clients': clients})


def should_clear_invoices(project):

    return (
        project.status == "completed"
        or project.total_paid >= project.total_spent
    )




# 📌 Project Update
from django.shortcuts import get_object_or_404, redirect, render
from .models import Project, Client
from .utils import delete_project_invoices   # if helper is in utils.py

def project_update(request, pk):

    project = get_object_or_404(Project, pk=pk)
    clients = Client.objects.all()

    if request.method == 'POST':

        project.client_id = request.POST.get('client')
        project.name = request.POST.get('name')
        project.budget = request.POST.get('budget')
        project.status = request.POST.get('status')

        project.save()

        # ==================================
        # DELETE ALL PROJECT INVOICES
        # WHEN PROJECT IS COMPLETED
        # ==================================
    if should_clear_invoices(project):
        delete_project_invoices(project)

        return redirect('project_list')

    return render(
        request,
        'billing/project/update.html',
        {
            'project': project,
            'clients': clients
        }
    )


# 📌 Project Delete
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    return render(request, 'billing/project/delete.html', {'project': project})






from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.urls import reverse
from decimal import Decimal
import urllib.parse


def project_detail(request, pk):

    project = get_object_or_404(
        Project.objects.select_related('client'),
        pk=pk
    )

    spends = project.spends.select_related(
        'floor', 'room', 'fullsemi'
    )

    payments = project.payments.order_by('date', 'id')

    # ✅ FAST database total (qty × rate)
    total_spent = spends.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('qty') * F('rate') * F('length') * F('width'),
                output_field=DecimalField()
            )
        )
    )['total'] or Decimal("0.00")

    running_total = Decimal("0.00")
    payment_rows = []

    for payment in payments:
        previous_paid = running_total
        running_total += payment.amount
        balance_after = project.budget - running_total

        # ✅ build public invoice link
        invoice_path = reverse('public_invoice', args=[payment.invoice_token])
        invoice_url = request.build_absolute_uri(invoice_path)

        # ✅ proper URL-encoded WhatsApp message
        message = (
            f"Hello {project.client.name}, "
            f"Your invoice is ready. Click to view: {invoice_url}"
        )
        encoded_message = urllib.parse.quote(message)

        whatsapp_url = f"https://wa.me/91{project.client.mobile_1}?text={encoded_message}"

        payment_rows.append({
            'id': payment.id,
            'date': payment.date,
            'previous_paid': previous_paid,
            'now_paid': payment.amount,
            'total_paid': running_total,
            'balance_after': balance_after,
            'mode': payment.get_payment_mode_display(),
            'whatsapp_url': whatsapp_url,  # ✅ IMPORTANT
        })

    balance = project.budget - running_total

    context = {
        'project': project,
        'spends': spends,
        'payment_rows': payment_rows,
        'total_spent': total_spent,
        'total_paid': running_total,
        'balance': balance,
    }

    return render(request, 'billing/project/detail.html', context)











# 📌 Floor List
def floor_list(request):
    floors = FloorType.objects.all().order_by('-id')
    return render(request, 'billing/floor/index.html', {'floors': floors})


# 📌 Floor Create
from django.http import JsonResponse
import json

@login_required
def floor_create(request):
    if request.method == 'POST':
        
        # ===== AJAX Request (from Quick Create modal) =====
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                
                if not name:
                    return JsonResponse({
                        'success': False,
                        'error': 'Floor name is required'
                    }, status=400)
                
                # Check duplicate
                if FloorType.objects.filter(name__iexact=name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'"{name}" already exists'
                    }, status=400)
                
                floor = FloorType.objects.create(name=name)
                
                return JsonResponse({
                    'success': True,
                    'id': floor.id,
                    'name': floor.name,
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid request'
                }, status=400)
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        # ===== Normal Form POST =====
        name = request.POST.get('name', '').strip()
        if name:
            FloorType.objects.get_or_create(name=name)
        return redirect('floor_list')

    return render(request, 'billing/floor/create.html')





# 📌 Floor Update
def floor_update(request, pk):
    floor = get_object_or_404(FloorType, pk=pk)

    if request.method == 'POST':
        floor.name = request.POST.get('name')
        floor.save()
        return redirect('floor_list')

    return render(request, 'billing/floor/update.html', {'floor': floor})


# 📌 Floor Delete
def floor_delete(request, pk):
    floor = get_object_or_404(FloorType, pk=pk)

    if request.method == 'POST':
        floor.delete()
        return redirect('floor_list')

    return render(request, 'billing/floor/delete.html', {'floor': floor})






# 📌 Room List
def room_list(request):
    rooms = RoomType.objects.all().order_by('-id')
    return render(request, 'billing/room/index.html', {'rooms': rooms})


# 📌 Room Create
import json
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def room_create(request):
    if request.method == 'POST':

        # ===== AJAX =====
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                name = data.get('name', '').strip()

                if not name:
                    return JsonResponse({
                        'success': False,
                        'error': 'Room name is required'
                    }, status=400)

                if RoomType.objects.filter(name__iexact=name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'"{name}" already exists'
                    }, status=400)

                room = RoomType.objects.create(name=name)

                return JsonResponse({
                    'success': True,
                    'id': room.id,
                    'name': room.name,
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)

        # ===== Normal POST =====
        name = request.POST.get('name', '').strip()
        if name:
            RoomType.objects.create(name=name)
        return redirect('room_list')

    return render(request, 'billing/room/create.html')


# 📌 Room Update
def room_update(request, pk):
    room = get_object_or_404(RoomType, pk=pk)

    if request.method == 'POST':
        room.name = request.POST.get('name')
        room.save()
        return redirect('room_list')

    return render(request, 'billing/room/update.html', {'room': room})


# 📌 Room Delete
def room_delete(request, pk):
    room = get_object_or_404(RoomType, pk=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('room_list')

    return render(request, 'billing/room/delete.html', {'room': room})









# 📌 FullSemi List
def fullsemi_list(request):
    fullsemis = FullSemi.objects.all().order_by('-id')
    return render(request, 'billing/fullsemi/index.html', {'fullsemis': fullsemis})


# 📌 FullSemi Create
@login_required
def fullsemi_create(request):
    if request.method == 'POST':

        # ===== AJAX =====
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                rate = data.get('rate', 0)

                if not name:
                    return JsonResponse({
                        'success': False,
                        'error': 'Series name is required'
                    }, status=400)

                if not rate or float(rate) <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Rate must be greater than 0'
                    }, status=400)

                if FullSemi.objects.filter(name__iexact=name).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'"{name}" already exists'
                    }, status=400)

                fs = FullSemi.objects.create(
                    name=name,
                    rate=Decimal(str(rate))
                )

                return JsonResponse({
                    'success': True,
                    'id': fs.id,
                    'name': fs.name,
                    'rate': str(fs.rate),
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)

        # ===== Normal POST =====
        name = request.POST.get('name', '').strip()
        rate = request.POST.get('rate', 0)
        if name and rate:
            FullSemi.objects.create(name=name, rate=rate)
        return redirect('fullsemi_list')

    return render(request, 'billing/fullsemi/create.html')


# 📌 FullSemi Update
def fullsemi_update(request, pk):
    fullsemi = get_object_or_404(FullSemi, pk=pk)

    if request.method == 'POST':
        fullsemi.name = request.POST.get('name')
        fullsemi.rate = request.POST.get('rate')
        fullsemi.save()
        return redirect('fullsemi_list')

    return render(request, 'billing/fullsemi/update.html', {'fullsemi': fullsemi})


# 📌 FullSemi Delete
def fullsemi_delete(request, pk):
    fullsemi = get_object_or_404(FullSemi, pk=pk)

    if request.method == 'POST':
        fullsemi.delete()
        return redirect('fullsemi_list')

    return render(request, 'billing/fullsemi/delete.html', {'fullsemi': fullsemi})





# # 📌 Spend List
# def spend_list(request):
#     client_id = request.GET.get('client')

#     spends = Spend.objects.none()

#     if client_id:
#         spends = (
#             Spend.objects
#             .select_related('project__client', 'floor', 'room', 'fullsemi')
#             .filter(project__client_id=client_id)
#             .order_by('-id')
#         )

#     clients = Client.objects.all()

#     return render(request, 'billing/spend/index.html', {
#         'spends': spends,
#         'clients': clients,
#         'selected_client': client_id,
#     })



# 📌 Spend List
# def spend_list(request):
#     client_id = request.GET.get('client')

#     spends = Spend.objects.none()

#     if client_id:
#         spends = (
#             Spend.objects
#             .select_related('project__client', 'floor', 'room', 'fullsemi')
#             .filter(project__client_id=client_id)
#             .order_by('-id')
#         )

#     clients   = Client.objects.all()
#     floors    = FloorType.objects.all()
#     rooms     = RoomType.objects.all()
#     fullsemis = FullSemi.objects.all()
#     projects  = Project.objects.select_related('client').all()

#     return render(request, 'billing/spend/index.html', {
#         'spends':          spends,
#         'clients':         clients,
#         'selected_client': client_id,

#         # ── For bulk edit dropdowns ──
#         'floors':    floors,
#         'rooms':     rooms,
#         'fullsemis': fullsemis,
#         'projects':  projects,
#     })



from decimal import Decimal, ROUND_HALF_UP

def spend_list(request):
    client_id = request.GET.get('client')

    spends = Spend.objects.none()
    total_spent = Decimal("0")

    if client_id:
        spends = (
            Spend.objects
            .select_related('project__client', 'floor', 'room', 'fullsemi')
            .filter(project__client_id=client_id)
            .order_by('-id')
        )

        total_spent = spends.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('qty') * F('rate') * F('length') * F('width'),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )
        )['total'] or Decimal("0")

        # Round to whole rupee
        total_spent = total_spent.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )

    clients   = Client.objects.all()
    floors    = FloorType.objects.all()
    rooms     = RoomType.objects.all()
    fullsemis = FullSemi.objects.all()
    projects  = Project.objects.select_related('client').all()

    return render(request, 'billing/spend/index.html', {
        'spends': spends,
        'clients': clients,
        'selected_client': client_id,

        'floors': floors,
        'rooms': rooms,
        'fullsemis': fullsemis,
        'projects': projects,

        'total_spent': total_spent,
    })


# views.py

from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from decimal import Decimal


@login_required
@require_POST
def spend_bulk_update(request):
    """Bulk update — per-row individual edits."""

    row_ids      = request.POST.getlist('row_id[]')
    row_floors   = request.POST.getlist('row_floor[]')
    row_rooms    = request.POST.getlist('row_room[]')
    row_fullsemis = request.POST.getlist('row_fullsemi[]')
    row_rates    = request.POST.getlist('row_rate[]')
    row_qtys     = request.POST.getlist('row_qty[]')
    row_units    = request.POST.getlist('row_unit[]')

    if not row_ids:
        messages.warning(request, 'No items to update.')
        return redirect(request.META.get('HTTP_REFERER', 'spend_list'))

    updated = 0

    for i, spend_id in enumerate(row_ids):
        try:
            spend = Spend.objects.get(id=spend_id)
        except Spend.DoesNotExist:
            continue

        # Floor
        floor_val = row_floors[i] if i < len(row_floors) else ''
        if floor_val:
            spend.floor_id = int(floor_val)

        # Room
        room_val = row_rooms[i] if i < len(row_rooms) else ''
        if room_val:
            spend.room_id = int(room_val)

        # FullSemi
        fs_val = row_fullsemis[i] if i < len(row_fullsemis) else ''
        if fs_val:
            spend.fullsemi_id = int(fs_val)

        # Rate
        rate_val = row_rates[i] if i < len(row_rates) else ''
        if rate_val:
            spend.rate = Decimal(rate_val)

        # Qty
        qty_val = row_qtys[i] if i < len(row_qtys) else ''
        if qty_val:
            spend.qty = Decimal(qty_val)

        # Unit
        unit_val = row_units[i] if i < len(row_units) else ''
        if unit_val:
            spend.unit = unit_val.strip()

        spend.save()  # triggers area/total recalc
        updated += 1

    messages.success(request, f'Successfully updated {updated} item(s).')

    return redirect(request.META.get('HTTP_REFERER', 'spend_list'))


@login_required
@require_POST
def spend_bulk_delete(request):
    """Bulk delete selected spend entries."""

    spend_ids = request.POST.getlist('spend_ids')

    if not spend_ids:
        messages.warning(request, 'No items selected.')
        return redirect('spend_index')

    deleted_count, _ = Spend.objects.filter(
        id__in=spend_ids
    ).delete()

    messages.success(
        request,
        f'Successfully deleted {deleted_count} items.'
    )

    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        return redirect(referer)
    return redirect('spend_index')





from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
import json

@require_POST
def check_duplicate_spend(request):

    data = json.loads(request.body)

    project_id = data.get("project")
    rows = data.get("rows", [])

    duplicates = []

    for row in rows:

        element = row.get("elements")
        floor = row.get("floor")
        room = row.get("room")
        length = row.get("length")
        width = row.get("width")

        qs = Spend.objects.filter(
            project_id=project_id,
            elements=element,
            floor_id=floor,
            room_id=room,
            length=length,
            width=width
        )

        if qs.exists():

            duplicates.append({
                "element": element,
                "floor": qs.first().floor.name if qs.first().floor else "",
                "room": qs.first().room.name if qs.first().room else "",
                "length": str(length),
                "width": str(width),
            })

    return JsonResponse({
        "duplicates": duplicates
    })



# 📌 Spend Create
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Spend, Project, FloorType, RoomType, FullSemi


def spend_create(request):

    projects = Project.objects.select_related('client').all()
    floors = FloorType.objects.all()
    rooms = RoomType.objects.all()
    fullsemis = FullSemi.objects.all()

    if request.method == "POST":

        project_id = request.POST.get("project")

        if not project_id:
            messages.error(request, "Please select a project.")
            return redirect("spend_create")

        floors_list = request.POST.getlist("floor[]")
        rooms_list = request.POST.getlist("room[]")
        fullsemis_list = request.POST.getlist("fullsemi[]")

        elements_list = request.POST.getlist("elements[]")
        descriptions_list = request.POST.getlist("description[]")

        lengths = request.POST.getlist("length[]")
        widths = request.POST.getlist("width[]")
        areas = request.POST.getlist("area[]")

        units = request.POST.getlist("unit[]")
        rates = request.POST.getlist("rate[]")

        qtys = request.POST.getlist("qty[]")
        totals = request.POST.getlist("total_amount[]")

        rows = []

        for i in range(len(elements_list)):

            if not elements_list[i]:
                continue

            try:
                length = Decimal(lengths[i]) if lengths[i] else None
                width = Decimal(widths[i]) if widths[i] else None
                area = Decimal(areas[i]) if areas[i] else None
                rate = Decimal(rates[i]) if rates[i] else None
                qty = Decimal(qtys[i]) if qtys[i] else Decimal("1")
                

            except InvalidOperation:
                continue

            rows.append(
                Spend(
                    project_id=project_id,
                    floor_id=floors_list[i] or None,
                    room_id=rooms_list[i] or None,
                    fullsemi_id=fullsemis_list[i] or None,
                    elements=elements_list[i],
                    description=descriptions_list[i],
                    length=length,
                    width=width,
                    area=area,
                    unit=units[i] if units else "sqft",
                    rate=rate,
                    qty=qty,
                    
                )
            )

        if rows:
            Spend.objects.bulk_create(rows)

        # update project budget
        project = Project.objects.get(id=project_id)
        project.budget += sum(r.total_amount for r in rows if r.total_amount)
        project.save()

        messages.success(request, "Spend entries created successfully.")
        return redirect("spend_list")

    return render(request, "billing/spend/create.html", {
        "projects": projects,
        "floors": floors,
        "rooms": rooms,
        "fullsemis": fullsemis
    })










# 📌 Spend Update
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Spend, Project, FloorType, RoomType, FullSemi


def spend_update(request, pk):

    spend = get_object_or_404(Spend, pk=pk)

    projects = Project.objects.select_related("client").all()
    floors = FloorType.objects.all()
    rooms = RoomType.objects.all()
    fullsemis = FullSemi.objects.all()

    if request.method == "POST":

        project_id = request.POST.get("project")

        if not project_id:
            messages.error(request, "Project is required.")
            return redirect("spend_update", pk=pk)

        # 🔹 Calculate OLD spend total for this record
        old_total = spend.total_amount or Decimal("0")

        floors_list = request.POST.getlist("floor[]")
        rooms_list = request.POST.getlist("room[]")
        fullsemi_list = request.POST.getlist("fullsemi[]")

        elements_list = request.POST.getlist("elements[]")
        description_list = request.POST.getlist("description[]")

        length_list = request.POST.getlist("length[]")
        width_list = request.POST.getlist("width[]")
        area_list = request.POST.getlist("area[]")

        rate_list = request.POST.getlist("rate[]")
        qty_list = request.POST.getlist("qty[]")
        total_list = request.POST.getlist("total_amount[]")

        unit_list = request.POST.getlist("unit[]")

        rows = []

        for i in range(len(elements_list)):

            if not elements_list[i]:
                continue

            try:
                length = Decimal(length_list[i]) if length_list[i] else None
                width = Decimal(width_list[i]) if width_list[i] else None
                area = Decimal(area_list[i]) if area_list[i] else None
                rate = Decimal(rate_list[i]) if rate_list[i] else None
                qty = Decimal(qty_list[i]) if qty_list[i] else Decimal("1")

            except (InvalidOperation, IndexError):
                continue

            rows.append(
                Spend(
                    project_id=project_id,
                    floor_id=floors_list[i] or None,
                    room_id=rooms_list[i] or None,
                    fullsemi_id=fullsemi_list[i] or None,
                    elements=elements_list[i],
                    description=description_list[i],
                    length=length,
                    width=width,
                    area=area,
                    rate=rate,
                    qty=qty,
                    unit=unit_list[i] if unit_list else "sqft",
                )
            )

        # 🔹 Delete old spend row
        Spend.objects.filter(pk=pk).delete()

        # 🔹 Create new rows
        Spend.objects.bulk_create(rows)

        # 🔹 Calculate new spend total
        new_total = sum(r.total_amount for r in rows if r.total_amount)

        project = Project.objects.get(id=project_id)

        # 🔹 Correct budget adjustment
        project.budget = project.budget - old_total + new_total
        project.save()

        messages.success(request, "Spend entries updated successfully.")
        return redirect("spend_list")

    return render(
        request,
        "billing/spend/update.html",
        {
            "spend": spend,
            "projects": projects,
            "floors": floors,
            "rooms": rooms,
            "fullsemis": fullsemis,
        },
    )



# 📌 Spend Delete
def spend_delete(request, pk):
    spend = get_object_or_404(Spend, pk=pk)

    if request.method == 'POST':

        project = spend.project
        amount = spend.total_amount

        spend.delete()

        # 🔥 Subtract from budget
        project.budget -= amount
        project.save()

        messages.success(request, "Spend deleted successfully.")
        return redirect('spend_list')

    return render(request, 'billing/spend/delete.html', {'spend': spend})






from .models import Project

def payment_list(request):
    project_id = request.GET.get('project')

    payments = Payment.objects.none()

    if project_id:
        payments = (
            Payment.objects
            .select_related('project__client')
            .filter(project_id=project_id)
            .order_by('-id')
        )

    projects = Project.objects.select_related('client')

    return render(request, 'billing/payment/index.html', {
        'payments': payments,
        'projects': projects,
        'selected_project': project_id,
    })



from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from datetime import date
from decimal import Decimal
from .models import Payment


def check_duplicate_payment(request):

    project_id = request.GET.get("project")
    amount = request.GET.get("amount")
    payment_mode = request.GET.get("payment_mode")

    try:
        amount = Decimal(amount)
    except:
        return JsonResponse({"duplicate": False})

    duplicate = Payment.objects.filter(
        project_id=project_id,
        amount=amount,
        payment_mode=payment_mode
    ).exists()

    return JsonResponse({"duplicate": duplicate})


# 📌 Payment Create
def payment_create(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        Payment.objects.create(
            project_id=request.POST.get('project'),
            amount=request.POST.get('amount'),
            payment_mode=request.POST.get('payment_mode'),
        )
        return redirect('payment_list')

    return render(request, 'billing/payment/create.html', {'projects': projects})


from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Payment, Project


def payment_update(request, pk):

    payment = get_object_or_404(Payment, pk=pk)

    projects = Project.objects.all()

    if request.method == "POST":

        old_project = payment.project
        old_amount = payment.amount or Decimal("0")

        new_project_id = request.POST.get("project")
        new_amount = request.POST.get("amount")
        payment_mode = request.POST.get("payment_mode")
        date = request.POST.get("date")
        try:
            new_amount = Decimal(new_amount)
        except:
            messages.error(request, "Invalid payment amount.")
            return redirect("payment_update", pk=pk)

        payment.project_id = new_project_id
        payment.amount = new_amount
        payment.payment_mode = payment_mode
        payment.date = date
        payment.save()

        new_project = Project.objects.get(id=new_project_id)

        # 🔹 Adjust project budget correctly
        if old_project == new_project:

            difference = new_amount - old_amount
            new_project.budget += difference
            new_project.save()

        else:

            # remove old payment from old project
            old_project.budget -= old_amount
            old_project.save()

            # add new payment to new project
            new_project.budget += new_amount
            new_project.save()

        messages.success(request, "Payment updated successfully.")
        return redirect("payment_list")

    return render(
        request,
        "billing/payment/update.html",
        {
            "payment": payment,
            "projects": projects,
        },
    )


# 📌 Payment Delete
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        payment.delete()
        return redirect('payment_list')

    return render(request, 'billing/payment/delete.html', {'payment': payment})








from django.db.models import Sum, Avg


# views.py

from django.db.models import Sum, Avg, Count, Q, Max
from django.shortcuts import render
from decimal import Decimal, ROUND_HALF_UP


def invoice_dashboard(request):

    client_id = request.GET.get("client")
    project_id = request.GET.get("project")

    clients = Client.objects.all().order_by("name")

    projects = Payment.objects.none()
    invoices = Payment.objects.none()

    # ✅ Initialize all stats
    stats = {
        'total_received': Decimal('0.00'),
        'total_gst_collected': Decimal('0.00'),
        'total_discount_given': Decimal('0.00'),
        'total_base_amount': Decimal('0.00'),
        'total_grand_total': Decimal('0.00'),
        'invoice_count': 0,
        'most_used_gst': Decimal('0.00'),
        'payment_mode_breakdown': {},
    }

    if client_id:
        projects = Project.objects.filter(
            client_id=client_id
        ).order_by('-id')

    if project_id:

        invoices = (
            Payment.objects
            .select_related('project', 'project__client')
            .filter(project_id=project_id)
            .order_by('-date', '-id')
        )

        # ✅ Calculate correct stats
        stats = _calculate_invoice_stats(invoices)

    return render(request, 'billing/invoice/dashboard.html', {
        'clients': clients,
        'projects': projects,
        'invoices': invoices,
        'selected_client': client_id,
        'selected_project': project_id,

        # ✅ Pass correct stats
        'stats': stats,

        # ✅ Keep backward compatibility
        'total_amount': stats['total_received'],
        'avg_gst': stats['most_used_gst'],
    })


def _calculate_invoice_stats(invoices):
    """
    Calculate correct invoice statistics.
    
    Payment.amount = actual cash received (not base amount)
    GST & discount are stored per payment to calculate grand total
    """

    total_received = Decimal('0.00')
    total_gst_collected = Decimal('0.00')
    total_discount_given = Decimal('0.00')
    total_grand_total = Decimal('0.00')
    total_base_amount = Decimal('0.00')
    invoice_count = 0
    gst_rates = []
    payment_modes = {}

    for payment in invoices:
        invoice_count += 1

        # ✅ Amount received in this payment
        received = Decimal(str(payment.amount or 0))
        total_received += received

        # ✅ Track payment mode breakdown
        mode = payment.get_payment_mode_display()
        payment_modes[mode] = payment_modes.get(mode, Decimal('0')) + received

        # ✅ Track GST rate used
        if payment.gst_rate:
            gst_rates.append(Decimal(str(payment.gst_rate)))

    # ✅ Most used GST rate (mode, not average)
    # Because using average of 18%, 18%, 0% = 12% which is wrong
    most_used_gst = Decimal('0.00')
    if gst_rates:
        from collections import Counter
        gst_counter = Counter([str(r) for r in gst_rates])
        most_common_gst = gst_counter.most_common(1)[0][0]
        most_used_gst = Decimal(most_common_gst)

    return {
        'total_received': total_received.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_gst_collected': total_gst_collected.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_discount_given': total_discount_given.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_grand_total': total_grand_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_base_amount': total_base_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'invoice_count': invoice_count,
        'most_used_gst': most_used_gst,
        'payment_mode_breakdown': payment_modes,
        'unique_gst_rates': sorted(set(str(r) for r in gst_rates)),
    }



def client_invoice_list(request):

    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    # Base queryset
    invoices = (
        Payment.objects
        .filter(
            project__client_id=client_id,
            invoice_archived=False
        )
        .exclude(invoice_pdf="")
        .exclude(invoice_pdf__isnull=True)
        .select_related("project")
    )

    # ---- Search Filter ----
    query = request.GET.get("q", "").strip()
    if query:
        invoices = invoices.filter(
            project__name__icontains=query
        )

    # ---- Project Filter ----
    selected_project = request.GET.get("project", "")
    if selected_project:
        invoices = invoices.filter(
            project_id=selected_project
        )

    # ---- Sort (Newest / Oldest) ----
    current_sort = request.GET.get("sort", "newest")
    if current_sort == "oldest":
        invoices = invoices.order_by("date")
    else:
        invoices = invoices.order_by("-date")

    # ---- Get unique projects for filter dropdown ----
    projects = (
        Payment.objects
        .filter(
            project__client_id=client_id,
            invoice_archived=False
        )
        .exclude(invoice_pdf="")
        .exclude(invoice_pdf__isnull=True)
        .values_list("project", flat=True)
        .distinct()
    )


    project_list = (
        Project.objects
        .filter(id__in=projects)
        .order_by("name")
    )

    return render(
        request,
        "billing/invoice/client_invoice_list.html",
        {
            "invoices": invoices,
            "projects": project_list,
            "selected_project": selected_project,
            "current_sort": current_sort,
        }
    )


def archive_invoice(request, pk):

    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    payment = get_object_or_404(
        Payment,
        pk=pk,
        project__client_id=client_id
    )

    payment.invoice_archived = True

    payment.save(
        update_fields=["invoice_archived"]
    )

    messages.success(
        request,
        "Invoice archived successfully."
    )

    return redirect("client_invoice_list")



def unarchive_invoice(request, pk):

    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    payment = get_object_or_404(
        Payment,
        pk=pk,
        project__client_id=client_id
    )

    payment.invoice_archived = False

    payment.save(
        update_fields=["invoice_archived"]
    )

    messages.success(
        request,
        "Invoice restored successfully."
    )

    return redirect("invoice_archive")








def invoice_archive(request):

    client_id = request.session.get("client_id")
    if not client_id:
        return redirect("client_login")

    # Base queryset
    invoices = (
        Payment.objects
        .filter(project__client_id=client_id, invoice_archived=True)
        .exclude(invoice_pdf="")
        .exclude(invoice_pdf__isnull=True)
        .select_related("project", "project__client")
    )

    # ---- Search ----
    query = request.GET.get("q", "").strip()
    if query:
        invoices = invoices.filter(
            Q(project__name__icontains=query) |
            Q(project__client__name__icontains=query)
        )

    # ---- Client Filter ----
    selected_client = request.GET.get("client", "")
    if selected_client:
        invoices = invoices.filter(project__client_id=selected_client)

    # ---- Project Filter ----
    selected_project = request.GET.get("project", "")
    if selected_project:
        invoices = invoices.filter(project_id=selected_project)

    # ---- Sort ----
    current_sort = request.GET.get("sort", "newest")
    invoices = invoices.order_by("date" if current_sort == "oldest" else "-date")



    archived_ids = (
        Payment.objects
        .filter(project__client_id=client_id, invoice_archived=True)
        .exclude(invoice_pdf="")
        .exclude(invoice_pdf__isnull=True)
    )

    project_list = Project.objects.filter(
        id__in=archived_ids.values_list("project_id", flat=True)
    ).order_by("name")

    client_list = Client.objects.filter(
        id__in=project_list.values_list("client_id", flat=True)
    ).order_by("name")

    return render(request, "billing/invoice/invoice_archive.html", {
        "invoices": invoices,
        "projects": project_list,
        "clients": client_list,
        "selected_client": selected_client,
        "selected_project": selected_project,
        "current_sort": current_sort,
    })

@login_required
def delete_invoice_pdf(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    try:

        if (
            payment.invoice_pdf
            and os.path.exists(
                payment.invoice_pdf.path
            )
        ):
            os.remove(
                payment.invoice_pdf.path
            )

    except Exception as e:
        print(e)

    payment.invoice_pdf = None
    payment.invoice_locked = False

    payment.save(
        update_fields=[
            "invoice_pdf",
            "invoice_locked"
        ]
    )

    messages.success(
        request,
        "Invoice PDF deleted successfully."
    )

    return redirect(
        "invoice_archive"
    )


from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from datetime import datetime
import re
from django.urls import reverse
import urllib.parse




from collections import OrderedDict

# ═══════════════════════════════════════
# CUSTOM SORT ORDERS
# ═══════════════════════════════════════

FLOOR_ORDER = {
    'ground floor':  1,
    'first floor':   2,
    'second floor':  3,
    'third floor':   4,
    'fourth floor':  5,
    'fifth floor':   6,
    'false ceiling': 7,
    'total':         8,
}

ROOM_ORDER = {
    'living hall':   1,
    'kitchen':       2,
    'bedroom':       3,
    'kids bedroom':  4,
    'guest bedroom': 5,
    'utility':       6,
    'others':        7,
}


def get_floor_sort_key(floor_name):
    """
    Returns sort priority for a floor.
    Unknown floors get 99 (pushed to end).
    """
    if not floor_name:
        return 99

    name = floor_name.strip().lower()

    # Exact match
    if name in FLOOR_ORDER:
        return FLOOR_ORDER[name]

    # Partial match (e.g. "Ground Floor - Block A")
    for key, order in FLOOR_ORDER.items():
        if key in name:
            return order

    return 99


def get_room_sort_key(room_name):
    """
    Returns sort priority for a room.
    Unknown rooms get 99 (pushed to end).
    """
    if not room_name:
        return 99

    name = room_name.strip().lower()

    # Exact match
    if name in ROOM_ORDER:
        return ROOM_ORDER[name]

    # Partial match (e.g. "Kids Bedroom 2")
    for key, order in ROOM_ORDER.items():
        if key in name:
            return order

    return 99


def group_spends_by_floor_room(spends):
    """
    Groups spends by Floor → Room with custom ordering.
    Returns OrderedDict:
    {
        'Ground Floor': {
            'Living Hall': [spend1, spend2],
            'Kitchen': [spend3],
            ...
        },
        'First Floor': { ... },
    }
    """

    # ── Sort spends using custom keys ──
    sorted_spends = sorted(
        spends,
        key=lambda s: (
            get_floor_sort_key(
                s.floor.name if s.floor else ''
            ),
            get_room_sort_key(
                s.room.name if s.room else ''
            ),
            s.id,
        )
    )

    # ── Group into nested OrderedDict ──
    grouped = OrderedDict()

    for spend in sorted_spends:

        floor_name = spend.floor.name if spend.floor else 'Unassigned'
        room_name  = spend.room.name  if spend.room  else 'General'

        if floor_name not in grouped:
            grouped[floor_name] = OrderedDict()

        if room_name not in grouped[floor_name]:
            grouped[floor_name][room_name] = []

        grouped[floor_name][room_name].append(spend)

    return grouped


def build_invoice_context(request, payment):

    project = payment.project
    client  = project.client

    invoice_number = f"INV-{client.id}{payment.id}{payment.date.strftime('%d%m%Y')}"

    # client_name = re.sub(
    #     r'[^A-Za-z0-9]+', '',
    #     client.name.capitalize()
    # )[:20]

    client_name = client.name.strip()

    # Keep letters, numbers, spaces and dots
    client_name = re.sub(r'[^A-Za-z0-9.\s]', '', client_name)

    # Remove extra spaces
    client_name = re.sub(r'\s+', '_', client_name)

    client_name = client_name[:20]

    project_code = "invoice"
    date_str     = payment.date.strftime('%d-%m-%Y')

    invoice_filename = f"{client_name}-{project_code}-({date_str}).pdf"

    invoice_url = request.build_absolute_uri(
        reverse('public_invoice', args=[payment.invoice_token])
    )

    # ═══════════════════════════════════════
    # SPENDS — CUSTOM FLOOR + ROOM ORDER
    # ═══════════════════════════════════════

    spends_qs = project.spends.select_related(
        'floor', 'room', 'fullsemi'
    ).all()

    # ── Flat sorted list (for table rendering) ──
    spends = sorted(
        spends_qs,
        key=lambda s: (
            get_floor_sort_key(
                s.floor.name if s.floor else ''
            ),
            get_room_sort_key(
                s.room.name if s.room else ''
            ),
            s.id,
        )
    )

    # ── Grouped by Floor → Room ──
    grouped_spends = group_spends_by_floor_room(spends_qs)

    # ── Floor subtotals ──
    floor_totals = OrderedDict()
    for floor_name, rooms in grouped_spends.items():
        floor_total = sum(
            spend.total_amount or Decimal('0.00')
            for room_spends in rooms.values()
            for spend in room_spends
        )
        floor_totals[floor_name] = floor_total

    # ── Room subtotals (nested) ──
    room_totals = OrderedDict()
    for floor_name, rooms in grouped_spends.items():
        room_totals[floor_name] = OrderedDict()
        for room_name, room_spends in rooms.items():
            room_totals[floor_name][room_name] = sum(
                spend.total_amount or Decimal('0.00')
                for spend in room_spends
            )

    # ═══════════════════════════════════════
    # TOTALS & GST
    # ═══════════════════════════════════════

    total_spent = project.total_spent.quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    gst_rate = payment.gst_rate or (
        Decimal("0.00") if client.gst_number
        else Decimal("0.00")
    )

    gst_amount = (total_spent * gst_rate) / Decimal("100")

    discount_value = payment.discount_value or Decimal("0.00")
    discount_type  = payment.discount_type  or "percent"

    if discount_type == "percent":
        discount = (
            (total_spent + gst_amount) * discount_value / Decimal("100")
        )
    else:
        discount = discount_value

    grand_total = (
        total_spent + gst_amount - discount
    ).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    # ═══════════════════════════════════════
    # PAYMENT HISTORY
    # ═══════════════════════════════════════

    payments = project.payments.filter(
        date__lte=payment.date
    ).order_by('date', 'id')

    phone = f"91{client.mobile_1}"

    message = (
        f"Hello {client.name}, "
        f"Your invoice is ready. Click to view: {invoice_url}"
    )

    whatsapp_url = (
        f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
    )

    payment_rows    = []
    running_total   = Decimal("0.00")

    for p in payments:

        if not p.invoice_token:
            p.invoice_token = uuid.uuid4()
            p.save(update_fields=['invoice_token'])

        previous_paid = running_total
        running_total += p.amount

        payment_rows.append({
            'token':         p.invoice_token,
            'id':            p.id,
            'date':          p.date,
            'previous_paid': previous_paid,
            'now_paid':      p.amount,
            'total_paid':    running_total,
            'balance_after': grand_total - running_total,
            'mode':          p.get_payment_mode_display(),
        })

    # ═══════════════════════════════════════
    # RETURN CONTEXT
    # ═══════════════════════════════════════

    return {
        'project':       project,
        'payment':       payment,

        # Flat sorted spends
        'spends':        spends,

        # Grouped: Floor → Room → [spends]
        'grouped_spends': grouped_spends,

        # Subtotals
        'floor_totals':  floor_totals,
        'room_totals':   room_totals,

        'total_spent':   total_spent,
        'gst_rate':      gst_rate,
        'gst_amount':    gst_amount,
        'discount':      discount,
        'grand_total':   grand_total,

        'payment_rows':      payment_rows,
        'invoice_number':    invoice_number,
        'invoice_filename':  invoice_filename,
        'invoice_url':       invoice_url,
        'whatsapp_url':      whatsapp_url,
    }



import os
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Payment


@login_required
def freeze_invoice(request, pk):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "POST request required"
        })

    try:

        payment = get_object_or_404(
            Payment,
            pk=pk
        )

        data = json.loads(request.body)

        html = data.get("html")

        if not html:
            return JsonResponse({
                "success": False,
                "error": "No HTML received"
            })

        # ==========================
        # CREATE MEDIA/INVOICES
        # ==========================

        invoice_dir = settings.MEDIA_ROOT / "invoices"

        invoice_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ==========================
        # FILE NAME
        # ==========================

        filename = f"INV-{payment.id}.pdf"

        pdf_path = invoice_dir / filename

        # ==========================
        # DELETE OLD PDF
        # ==========================

        if pdf_path.exists():
            try:
                os.remove(pdf_path)
            except Exception:
                pass

        # ==========================
        # GENERATE PDF
        # ==========================

        generate_invoice_pdf(
            html,
            str(pdf_path)
        )

        # ==========================
        # SAVE DATABASE
        # ==========================

        payment.invoice_pdf = f"invoices/{filename}"
        payment.invoice_locked = True

        payment.save(
            update_fields=[
                "invoice_pdf",
                "invoice_locked"
            ]
        )

        print("=" * 50)
        print("INVOICE FROZEN")
        print("PAYMENT:", payment.id)
        print("PDF:", pdf_path)
        print("=" * 50)

        return JsonResponse({
            "success": True,
            "file": payment.invoice_pdf.url
        })

    except Exception as e:

        print("FREEZE ERROR:", str(e))

        return JsonResponse({
            "success": False,
            "error": str(e)
        })


from playwright.sync_api import sync_playwright

from playwright.sync_api import sync_playwright


def generate_invoice_pdf(html, output_path):

    with sync_playwright() as p:

        browser = p.chromium.launch()

        page = browser.new_page()

        page.set_content(
            html,
            wait_until="networkidle"
        )

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "10mm",
                "right": "10mm"
            }
        )

        browser.close()



@login_required
def payment_invoice(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related('project__client'),
        pk=pk
    )

    context = build_invoice_context(request, payment)
    context['is_public'] = False   # ✅ IMPORTANT
    return render(request, 'billing/payment/invoice.html', context)



def public_invoice(request, token):

    payment = get_object_or_404(
        Payment.objects.select_related('project__client'),
        invoice_token=token
    )

    context = build_invoice_context(request, payment)
    context['is_public'] = True   # ✅ IMPORTANT
    return render(request, 'billing/payment/invoice.html', context)




from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal

@login_required
@require_POST
def save_invoice_adjustments(request, pk):

    payment = get_object_or_404(Payment, pk=pk)

    try:
        gst_rate = Decimal(request.POST.get("gst_rate", "0"))
        discount_value = Decimal(request.POST.get("discount", "0"))
        discount_type = request.POST.get("discount_type", "percent")

        payment.gst_rate = gst_rate
        payment.discount_value = discount_value
        payment.discount_type = discount_type

        payment.save(update_fields=[
            "gst_rate",
            "discount_value",
            "discount_type"
        ])

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)





###################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from .models import Client, Quotation


QuotationForm = modelform_factory(
    Quotation,
    exclude=("created_at",)
)

@login_required
def qtn_client_index(request):

    search = request.GET.get("search", "")

    clients = QtnClient.objects.all()

    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(phone1__icontains=search) |
            Q(phone2__icontains=search) |
            Q(id__icontains=search)
        )

    return render(request, "billing/clientQT/index.html", {
        "clients": clients,
        "search": search
    })




# @login_required
# def qtn_client_create(request):

#     if request.method == "POST":

#         QtnClient.objects.create(
#             name=request.POST.get("name"),
#             phone1=request.POST.get("phone1"),
#             phone2=request.POST.get("phone2"),
#             email=request.POST.get("email"),
#             location=request.POST.get("location"),

#             gst=request.POST.get("gst"),

#             discount_percent=request.POST.get("discount_percent") or 0,
#             discount_amount=request.POST.get("discount_amount") or 0,
#             discount_mode=request.POST.get("discount_mode") or "percent",

#             notes=request.POST.get("notes"),

#             estimate_start_date=request.POST.get("estimate_start_date"),
#             estimate_end_date=request.POST.get("estimate_end_date"),
#         )

#         return redirect("qtn_client_index")

#     return render(request, "billing/clientQT/create.html")



@login_required
def qtn_client_create(request):

    if request.method == "POST":

        # ── Create Quotation Client ──
        qtn_client = QtnClient.objects.create(
            name             = request.POST.get("name")     or "",
            phone1           = request.POST.get("phone1")   or "",
            phone2           = request.POST.get("phone2")   or "",
            email            = request.POST.get("email")    or "",
            location         = request.POST.get("location") or "",
            gst              = request.POST.get("GST")      or "",
            discount_percent = request.POST.get("discount") or 0,
            discount_mode    = "percent",
            notes            = request.POST.get("notes")    or "",
        )

        sync_result = None  # Track what happened

        # ── Sync to Main Clients ──
        if request.POST.get("create_main_client"):
            try:
                existing = Client.objects.filter(
                    mobile_1=qtn_client.phone1
                ).first()

                if existing:
                    updated_fields = []

                    if not existing.name or existing.name == "Unknown":
                        existing.name = qtn_client.name
                        updated_fields.append("Name")

                    if not existing.email and qtn_client.email:
                        existing.email = qtn_client.email
                        updated_fields.append("Email")

                    if not existing.mobile_2 and qtn_client.phone2:
                        existing.mobile_2 = qtn_client.phone2
                        updated_fields.append("Phone 2")

                    if not existing.address or existing.address == "No Address":
                        existing.address = qtn_client.location
                        updated_fields.append("Address")

                    if not existing.gst_number and qtn_client.gst:
                        existing.gst_number = qtn_client.gst
                        updated_fields.append("GST")

                    if qtn_client.notes:
                        if existing.notes:
                            existing.notes += f"\n\n[QTN-{qtn_client.id}] {qtn_client.notes}"
                        else:
                            existing.notes = qtn_client.notes
                        updated_fields.append("Notes")

                    if updated_fields:
                        existing.save()
                        sync_result = {
                            "type": "updated",
                            "name": existing.name,
                            "phone": qtn_client.phone1,
                            "fields": updated_fields,
                        }
                    else:
                        sync_result = {
                            "type": "exists",
                            "name": existing.name,
                            "phone": qtn_client.phone1,
                        }

                else:
                    Client.objects.create(
                        name       = qtn_client.name             or "Unknown",
                        mobile_1   = qtn_client.phone1           or "0000000000",
                        mobile_2   = qtn_client.phone2           or "",
                        address    = qtn_client.location         or "No Address",
                        email      = qtn_client.email            or "",
                        notes      = qtn_client.notes            or "",
                        gst_number = qtn_client.gst              or "",
                        discount   = qtn_client.discount_percent or 0,
                    )
                    sync_result = {
                        "type": "created",
                        "name": qtn_client.name,
                    }

            except Exception as e:
                import traceback
                traceback.print_exc()
                sync_result = {
                    "type": "error",
                    "error": str(e),
                }

        # ── Build response based on result ──
        if sync_result:
            if sync_result["type"] == "error":
                # Stay on page, show error
                messages.error(
                    request,
                    f"⚠️ Quotation client '{qtn_client.name}' was created, "
                    f"but Main Client sync failed: {sync_result['error']}"
                )
                return render(request, "billing/clientQT/create.html", {
                    "sync_result": sync_result,
                    "created_client": qtn_client,
                })

            elif sync_result["type"] == "exists":
                messages.warning(
                    request,
                    f"✅ Quotation client created. "
                    f"Main client '{sync_result['name']}' already exists "
                    f"with phone {sync_result['phone']} — no updates needed."
                )

            elif sync_result["type"] == "updated":
                fields_str = ", ".join(sync_result["fields"])
                messages.info(
                    request,
                    f"✅ Quotation client created. "
                    f"Existing main client '{sync_result['name']}' updated: {fields_str}"
                )

            elif sync_result["type"] == "created":
                messages.success(
                    request,
                    f"✅ '{sync_result['name']}' created in both Quotation and Main systems."
                )

        else:
            messages.success(
                request,
                f"✅ '{qtn_client.name}' created as Quotation Client."
            )

        return redirect("qtn_client_index")

    return render(request, "billing/clientQT/create.html")







@login_required
def qtn_client_update(request, id):

    client = get_object_or_404(QtnClient, id=id)

    if request.method == "POST":

        client.name = request.POST.get("name")
        client.phone1 = request.POST.get("phone1")
        client.phone2 = request.POST.get("phone2")
        client.email = request.POST.get("email")
        client.location = request.POST.get("location")

        # FIXED FIELD NAME
        client.gst = request.POST.get("gst")

        client.discount_percent = request.POST.get("discount_percent") or 0
        client.discount_amount = request.POST.get("discount_amount") or 0
        client.discount_mode = request.POST.get("discount_mode") or "percent"

        client.notes = request.POST.get("notes")

        client.estimate_start_date = request.POST.get("estimate_start_date")
        client.estimate_end_date = request.POST.get("estimate_end_date")

        client.save()

        return redirect("qtn_client_index")

    return render(
        request,
        "billing/clientQT/update.html",
        {
            "client": client
        }
    )


@login_required
def qtn_client_delete(request, id):

    client = get_object_or_404(QtnClient, id=id)

    if request.method == "POST":
        client.delete()
        return redirect("qtn_client_index")

    return render(
        request,
        "billing/clientQT/confirm_delete.html",
        {"client": client},
    )



from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import QuotationItem


@login_required
def quotation_index(request):

    search = request.GET.get("search", "")

    quotations = (
        QuotationItem.objects
        .values(
            "client__id",
            "client__name",
            "client__phone1",
            "client__email",
        )
        .annotate(
            total_qty=Sum("qty"),
            grand_total=Sum("total"),
        )
    )

    if search:
        quotations = quotations.filter(
            Q(client__name__icontains=search) |
            Q(client__phone1__icontains=search)
        )

    quotations = quotations.order_by("-client__id")

    return render(
        request,
        "billing/quotation/index.html",
        {
            "quotations": quotations,
            "search": search
        }
    )


from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import QtnClient, QuotationItem, Image, FullSemi


from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import QtnClient, QuotationItem, Image, FullSemi


@login_required
def quotation_create(request):

    if request.method == "POST":

        client_id = request.POST.get("client")

        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        # ✅ Update client dates
        if client_id:
            QtnClient.objects.filter(id=client_id).update(
                estimate_start_date=start_date,
                estimate_end_date=end_date,
            )

        # 🔥 GET ALL LIST DATA
        floors = request.POST.getlist("floor[]")
        locations = request.POST.getlist("location[]")
        elements = request.POST.getlist("element[]")

        images = request.POST.getlist("image[]")
        fullsemis = request.POST.getlist("full_semi[]")

        core_materials = request.POST.getlist("core_material[]")
        finish_materials = request.POST.getlist("finish_material[]")
        brands = request.POST.getlist("brand[]")
        specifications = request.POST.getlist("specification[]")

        units = request.POST.getlist("unit[]")
        lengths = request.POST.getlist("length[]")
        widths = request.POST.getlist("width[]")
        qtys = request.POST.getlist("qty[]")

        # 🔥 IMPORTANT (manual rate)
        rate_inputs = request.POST.getlist("rate[]")

        # 🔥 preload fullsemi rates (performance)
        fullsemi_rates = {
            f.id: f.rate for f in FullSemi.objects.all()
        }

        quotation_rows = []

        for i in range(len(elements)):

            if not elements[i]:
                continue

            # ✅ SAFE DECIMAL PARSE
            try:
                length = Decimal(lengths[i] or 0)
                width = Decimal(widths[i] or 0)
                qty = Decimal(qtys[i] or 1)
            except InvalidOperation:
                continue

            area = length * width

            # 🔥 RATE LOGIC (FIXED 🔥)
            try:
                price = Decimal(rate_inputs[i] or 0)
            except (InvalidOperation, IndexError):
                price = Decimal("0.00")

            fullsemi_id = fullsemis[i] if i < len(fullsemis) else None

            # fallback to preset
            if price <= 0 and fullsemi_id:
                price = fullsemi_rates.get(int(fullsemi_id), Decimal("0.00"))

            # optional: skip invalid rows
            if price <= 0:
                continue

            # checkbox
            end_floor = request.POST.get(f"floor_end_{i}") == "1"

            total = area * price * qty

            quotation_rows.append(
                QuotationItem(
                    client_id=client_id,

                    floor=floors[i] if i < len(floors) else "",
                    location=locations[i] if i < len(locations) else "",
                    element=elements[i],

                    image_id=images[i] if i < len(images) and images[i] else None,
                    full_semi_id=fullsemi_id,

                    core_material=core_materials[i] if i < len(core_materials) else "",
                    finish_material=finish_materials[i] if i < len(finish_materials) else "",
                    brand=brands[i] if i < len(brands) else "",
                    specification=specifications[i] if i < len(specifications) else "",

                    unit=units[i] if i < len(units) else "sqft",

                    length=length,
                    width=width,
                    area=area,

                    price=price,   # ✅ FIXED
                    qty=qty,
                    total=total,

                    end=end_floor,
                )
            )

        # 🔥 BULK CREATE
        if quotation_rows:
            QuotationItem.objects.bulk_create(quotation_rows, batch_size=500)

        return redirect("quotation_index")

    return render(request, "billing/quotation/create.html", {
        "clients": QtnClient.objects.all(),
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
        "max_fields": 10000,  # frontend can use this to limit dynamic rows
        "previous_specs": list(
            QuotationItem.objects
            .exclude(specification="")
            .values_list("specification", flat=True)
            .distinct()[:200]
        )
    })



from decimal import Decimal
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import QtnClient, QuotationItem, Image, FullSemi


# from decimal import Decimal, InvalidOperation
# from django.db import transaction
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .models import QtnClient, QuotationItem, Image, FullSemi


# @login_required
# def quotation_update(request, id):

#     rows = QuotationItem.objects.filter(client_id=id)

#     if not rows.exists():
#         return redirect("quotation_index")

#     client_id = id

#     if request.method == "POST":

#         start_date = request.POST.get("estimate_start_date")
#         end_date = request.POST.get("estimate_end_date")

#         # ✅ update client dates
#         QtnClient.objects.filter(id=client_id).update(
#             estimate_start_date=start_date,
#             estimate_end_date=end_date,
#         )

#         # 🔥 GET ALL LISTS
#         floors = request.POST.getlist("floor[]")
#         locations = request.POST.getlist("location[]")
#         elements = request.POST.getlist("element[]")

#         images = request.POST.getlist("image[]")
#         fullsemis = request.POST.getlist("full_semi[]")

#         core_materials = request.POST.getlist("core_material[]")
#         finish_materials = request.POST.getlist("finish_material[]")
#         brands = request.POST.getlist("brand[]")
#         specifications = request.POST.getlist("specification[]")

#         units = request.POST.getlist("unit[]")
#         lengths = request.POST.getlist("length[]")
#         widths = request.POST.getlist("width[]")
#         qtys = request.POST.getlist("qty[]")

#         # 🔥 IMPORTANT (manual rate)
#         rate_inputs = request.POST.getlist("rate[]")

#         # 🔥 preload rates
#         fullsemi_rates = {f.id: f.rate for f in FullSemi.objects.all()}

#         quotation_rows = []

#         for i in range(len(elements)):

#             if not elements[i]:
#                 continue

#             # ✅ SAFE PARSE
#             try:
#                 length = Decimal(lengths[i] or 0)
#                 width = Decimal(widths[i] or 0)
#                 qty = Decimal(qtys[i] or 1)
#             except InvalidOperation:
#                 continue

#             area = length * width

#             # 🔥 RATE FIX (CRITICAL 🔥)
#             try:
#                 price = Decimal(rate_inputs[i] or 0)
#             except (InvalidOperation, IndexError):
#                 price = Decimal("0.00")

#             fullsemi_id = fullsemis[i] if i < len(fullsemis) else None

#             # fallback to preset
#             if price <= 0 and fullsemi_id:
#                 price = fullsemi_rates.get(int(fullsemi_id), Decimal("0.00"))

#             # optional skip invalid
#             if price <= 0:
#                 continue

#             # checkbox
#             end_floor = request.POST.get(f"floor_end_{i}") == "1"

#             total = area * price * qty

#             quotation_rows.append(
#                 QuotationItem(
#                     client_id=client_id,

#                     floor=floors[i].strip() if i < len(floors) else "",
#                     location=locations[i].strip() if i < len(locations) else "",
#                     element=elements[i].strip(),

#                     image_id=int(images[i]) if i < len(images) and images[i] else None,
#                     full_semi_id=fullsemi_id,

#                     core_material=core_materials[i] if i < len(core_materials) else "",
#                     finish_material=finish_materials[i] if i < len(finish_materials) else "",
#                     brand=brands[i] if i < len(brands) else "",
#                     specification=specifications[i] if i < len(specifications) else "",

#                     unit=units[i] if i < len(units) else "sqft",

#                     length=length,
#                     width=width,
#                     area=area,

#                     price=price,  # ✅ FIXED
#                     qty=qty,
#                     total=total,

#                     end=end_floor,
#                 )
#             )

#         # 🔥 REPLACE OLD DATA SAFELY
#         with transaction.atomic():
#             rows.delete()
#             if quotation_rows:
#                 QuotationItem.objects.bulk_create(quotation_rows, batch_size=500)

#         return redirect("quotation_index")

#     return render(request, "billing/quotation/update.html", {
#         "quotation_rows": rows,
#         "clients": QtnClient.objects.all(),
#         "images": Image.objects.all(),
#         "fullsemis": FullSemi.objects.all(),
#         "previous_specs": list(
#             QuotationItem.objects
#             .exclude(specification="")
#             .values_list("specification", flat=True)
#             .distinct()[:200]
#         )
#     })





from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import QtnClient, QuotationItem, Image, FullSemi


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import QtnClient, QuotationItem

@login_required
def quotation_update(request, client_id):

    client = get_object_or_404(QtnClient, id=client_id)

    rows = (
        QuotationItem.objects
        .filter(client_id=client_id)
        .select_related('client', 'image', 'full_semi')
        .order_by('sort_order', 'id')
    )

    if not rows.exists():
        return redirect("quotation_index")

    # 🔥 HANDLE UPDATE (ONLY CLIENT INFO)
    if request.method == "POST":

        new_client_id = request.POST.get("client")
        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        # ✅ Update client reference (if changed)
        if new_client_id and str(new_client_id) != str(client.id):
            new_client = get_object_or_404(QtnClient, id=new_client_id)

            # 🔥 Move all rows to new client
            rows.update(client=new_client)
            client = new_client  # update reference

        # ✅ Update dates
        client.estimate_start_date = start_date
        client.estimate_end_date = end_date
        client.save(update_fields=["estimate_start_date", "estimate_end_date"])

        return redirect("quotation_index")

    # -------------------------
    # Display
    # -------------------------
    subtotal = sum((r.total for r in rows), Decimal("0.00"))

    return render(request, "billing/quotation/update.html", {
        "client": client,
        "rows": rows,
        "subtotal": subtotal,
        "row_count": rows.count(),
        "clients": QtnClient.objects.all(),  # 🔥 for dropdown
    })


@login_required
def quotation_row_edit(request, row_id):
    """
    Edit a SINGLE quotation row
    Only this one row is loaded and saved
    """
    row = get_object_or_404(
        QuotationItem.objects.select_related('client', 'image', 'full_semi'),
        id=row_id
    )
    client = row.client

    if request.method == "POST":
        
        # Parse values
        try:
            length = Decimal(request.POST.get('length', 0) or 0)
            width = Decimal(request.POST.get('width', 0) or 0)
            qty = Decimal(request.POST.get('qty', 1) or 1)
        except InvalidOperation:
            length = Decimal("0")
            width = Decimal("0")
            qty = Decimal("1")

        area = length * width

        # Rate
        try:
            price = Decimal(request.POST.get('rate', 0) or 0)
        except (InvalidOperation, TypeError):
            price = Decimal("0.00")

        # Fallback to preset rate
        fullsemi_id = request.POST.get('full_semi') or None
        if price <= 0 and fullsemi_id:
            try:
                fs = FullSemi.objects.get(id=int(fullsemi_id))
                price = fs.rate
            except (FullSemi.DoesNotExist, ValueError):
                pass

        total = area * price * qty

        # Update fields
        row.floor = request.POST.get('floor', '')
        row.location = request.POST.get('location', '')
        row.element = request.POST.get('element', '')
        row.unit = request.POST.get('unit', 'sqft')
        row.specification = request.POST.get('specification', '')
        row.core_material = request.POST.get('core_material', '')
        row.finish_material = request.POST.get('finish_material', '')
        row.brand = request.POST.get('brand', '')

        image_id = request.POST.get('image')
        row.image_id = int(image_id) if image_id else None

        row.full_semi_id = int(fullsemi_id) if fullsemi_id else None

        row.length = length
        row.width = width
        row.area = area
        row.price = price
        row.qty = qty
        row.total = total
        row.end = request.POST.get('end') == '1'

        row.save()

        # Redirect back to the list
        next_url = request.POST.get('next', '')
        if next_url == 'stay':
            # Stay on same edit page (save & continue)
            return redirect('quotation_row_edit', row_id=row.id)
        
        return redirect('quotation_update', client_id=client.id)

    return render(request, "billing/quotation/row_edit.html", {
        "row": row,
        "client": client,
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
        "previous_specs": list(
            QuotationItem.objects
            .filter(client=client)
            .exclude(specification="")
            .values_list("specification", flat=True)
            .distinct()[:100]
        ),
        # Next and previous row for navigation
        "next_row": QuotationItem.objects.filter(
            client=client, id__gt=row.id
        ).order_by('id').first(),
        "prev_row": QuotationItem.objects.filter(
            client=client, id__lt=row.id
        ).order_by('-id').first(),
    })



@login_required
def quotation_delete(request, id):

    client = get_object_or_404(QtnClient, id=id)

    if request.method == "POST":

        # delete quotation rows
        client.quotation_items.all().delete()

        # delete quotation records
        client.quotations.all().delete()

        # optional: delete client itself
        client.delete()

        return redirect("quotation_index")

    return render(
        request,
        "billing/quotation/confirm_delete.html",
        {"client": client},
    )


from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import QtnClient, QuotationItem

from collections import defaultdict

@login_required
def quotation_detail(request, client_id):

    rows = (
        QuotationItem.objects
        .select_related("client", "image", "full_semi")
        .filter(client_id=client_id)
        .order_by("floor", "location")
    )

    if not rows.exists():
        return redirect("quotation_index")

    client = rows.first().client


    grouped_data = defaultdict(lambda: defaultdict(list))

    for r in rows:
        floor = r.floor or "Other"
        location = r.location or "General"
        grouped_data[floor][location].append(r)

    # ✅ CONVERT TO NORMAL DICT (IMPORTANT)
    grouped_data = {
        floor: dict(locations)
        for floor, locations in grouped_data.items()
    }

    # -------------------------
    # Totals (same as before)
    # -------------------------
    subtotal = sum((r.total for r in rows), Decimal("0.00"))

    gst_rate = Decimal(client.gst or 0)
    gst_amount = (subtotal * gst_rate) / Decimal("100")

    total_with_gst = subtotal + gst_amount

    discount_mode = client.discount_mode or "amount"

    if discount_mode == "percent":
        discount_percent = Decimal(client.discount_percent or 0)
        discount_amount = (subtotal * discount_percent) / Decimal("100")
    else:
        discount_amount = Decimal(client.discount_amount or 0)
        discount_percent = (discount_amount / subtotal * 100) if subtotal else 0

    grand_total = max(total_with_gst - discount_amount, Decimal("0.00"))

    return render(request, "billing/quotation/detail.html", {
        "client": client,
        "rows": rows,  # keep original if needed
        "grouped_data": grouped_data,  # 🔥 NEW

        "subtotal": round(subtotal, 2),
        "gst_rate": gst_rate,
        "gst_amount": round(gst_amount, 2),
        "discount_amount": round(discount_amount, 2),
        "discount_percent": round(discount_percent, 2),
        "discount_mode": discount_mode,
        "grand_total": round(grand_total, 2),
    })









# @login_required
# def quotation_preview(request, client_id):

#     client = get_object_or_404(QtnClient, id=client_id)

#     rows = QuotationItem.objects.filter(
#         client_id=client_id
#     ).order_by("id")

#     subtotal = sum(r.total for r in rows)

#     gst_rate = Decimal(client.gst or 0)
#     gst_amount = (subtotal * gst_rate) / Decimal("100")

#     total_with_gst = subtotal + gst_amount

#     discount = client.discount_amount or Decimal("0.00")

#     grand_total = total_with_gst - discount

#     return render(
#         request,
#         "billing/quotation/pdf.html",
#         {
#             "client": client,
#             "rows": rows,
#             "subtotal": subtotal,
#             "gst_rate": gst_rate,
#             "gst_amount": gst_amount,
#             "grand_total": grand_total,
#             "preview": True
#         }
#     )



# import json
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required

# @require_POST
# @login_required
# def save_quotation_order(request, client_id):

#     try:
#         data = json.loads(request.body.decode("utf-8"))

#         order = data.get("order", [])

#         for index, item_id in enumerate(order):

#             QuotationItem.objects.filter(
#                 id=int(item_id),
#                 client_id=client_id
#             ).update(sort_order=index)

#         return JsonResponse({
#             "status": "success",
#             "message": "Order saved"
#         })

#     except Exception as e:

#         print("ORDER SAVE ERROR:", e)   # ← IMPORTANT DEBUG

#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=400)



from io import BytesIO
from datetime import date
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from PyPDF2 import PdfMerger
from xhtml2pdf import pisa
import os
from django.db.models.functions import Lower
from django.db.models import Case, When, Value, IntegerField



from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Case, When, Value, IntegerField, Max
from django.db.models.functions import Lower
from datetime import date
from io import BytesIO
import os
from PyPDF2 import PdfMerger
from xhtml2pdf import pisa




from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Max
from django.db.models.functions import Lower
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date
from io import BytesIO
import os
import json
from PyPDF2 import PdfMerger
from xhtml2pdf import pisa


def fetch_resources(uri, rel):
    """Callback to allow xhtml2pdf to access local files"""
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = uri
    return path


@login_required
def quotation_pdf(request, client_id):
    """
    GET: Preview/Edit page with drag & drop
    POST: Generate merged PDF with custom order
    """

    client = get_object_or_404(QtnClient, id=client_id)

    # ── Parse custom order ──
    custom_order = None
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            custom_order = data.get("order", [])
        except Exception:
            custom_order = request.POST.getlist("order[]")

    # ── Fetch rows ──
    rows = list(
        QuotationItem.objects
        .filter(client_id=client_id)
        .annotate(
            floor_lower=Lower("floor"),
            location_lower=Lower("location"),
            floor_end=Max("end")
        )
        .order_by(
            "floor_end",
            "floor_lower",
            "location_lower",
            "sort_order",
            "id"
        )
    )

    # ── Apply custom order ──
    if custom_order:
        rows_dict    = {str(r.id): r for r in rows}
        ordered_rows = [rows_dict[str(i)] for i in custom_order if str(i) in rows_dict]
        remaining    = [r for r in rows if r not in ordered_rows]
        rows         = ordered_rows + remaining

    # ── Calculate totals ──
    subtotal       = sum((r.total for r in rows), Decimal("0.00"))
    gst_rate       = Decimal(client.gst or 0)
    gst_amount     = (subtotal * gst_rate) / Decimal("100")
    total_with_gst = subtotal + gst_amount

    if client.discount_mode == "percent":
        percent         = Decimal(client.discount_percent or 0)
        discount_amount = (subtotal * percent) / Decimal("100")
    else:
        discount_amount = Decimal(client.discount_amount or 0)

    grand_total      = max(total_with_gst - discount_amount, Decimal("0.00"))
    quotation_number = f"QTN-{client.id}-{date.today().strftime('%m%y')}"

    context = {
        "client":           client,
        "rows":             rows,
        "total_amount":     subtotal,
        "gst_rate":         gst_rate,
        "gst_amount":       gst_amount,
        "discount":         discount_amount,
        "grand_total":      grand_total,
        "quotation_number": quotation_number,
        "total_with_gst":   total_with_gst,
        "today":            date.today(),
    }

    # ── GET: Preview ──
    if request.method == "GET":
        if request.GET.get("print") == "1":
            context["print_mode"] = True
            return render(request, "billing/quotation/pdf_print.html", context)
        context["edit_mode"] = True
        return render(request, "billing/quotation/pdf.html", context)

    # ── POST: Generate PDF ──

    # 1. Render HTML
    template = get_template("billing/quotation/pdf_print.html")
    html     = template.render(context)

    # 2. Generate quotation PDF
    quotation_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=quotation_buffer,
        link_callback=fetch_resources
    )

    if pisa_status.err:
        return JsonResponse({"error": "PDF generation failed"}, status=500)

    quotation_buffer.seek(0)

    # 3. Merge front + quotation + back
    front_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "front.pdf")
    back_pdf  = os.path.join(settings.MEDIA_ROOT, "pdfs",  "back.pdf")

    merger = PdfMerger()

    if os.path.exists(front_pdf):
        merger.append(front_pdf)

    merger.append(quotation_buffer)

    if os.path.exists(back_pdf):
        merger.append(back_pdf)

    final_buffer = BytesIO()
    merger.write(final_buffer)
    merger.close()
    final_buffer.seek(0)

    # 4. Professional filename
    filename = _build_quotation_filename(client, quotation_number)

    response = HttpResponse(final_buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ════════════════════════════════════════════════════
#  FILENAME HELPER
# ════════════════════════════════════════════════════

def _build_quotation_filename(client, quotation_number):
    """
    Output: HomeDenInterior_Quote_Rajesh-Kumar_QTN-42-0124.pdf
    """
    import re
    import unicodedata

    # ── Clean client name ──
    raw_name = getattr(client, 'name', 'Client') or 'Client'

    name = unicodedata.normalize('NFKD', raw_name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = name.strip().title()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'-{2,}', '-', name)
    name = name[:20].strip('-')

    # ── Clean quotation number ──
    qtn_ref = re.sub(r'[^\w-]', '', str(quotation_number))

    # ── Assemble ──
    # HomeDenInteriorFirm_Quote_Rajesh-Kumar_QTN-42-0124.pdf
    filename = f"HomeDenInteriorFirm_Quote_{name}_{qtn_ref}.pdf"

    return filename

# # @login_required
# def quotation_pdf_debug(request, client_id):
#     import traceback
#     from io import BytesIO
#     import os

#     results = {}

#     # ── Step 1: Check PDF files ──
#     front_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "front.pdf")
#     back_pdf  = os.path.join(settings.MEDIA_ROOT, "pdfs", "back.pdf")

#     results['front_pdf_exists'] = os.path.exists(front_pdf)
#     results['back_pdf_exists']  = os.path.exists(back_pdf)
#     results['front_pdf_size']   = os.path.getsize(front_pdf) if results['front_pdf_exists'] else 0
#     results['back_pdf_size']    = os.path.getsize(back_pdf)  if results['back_pdf_exists']  else 0

#     # ── Step 2: Check template tag loads ──
#     try:
#         from billing.templatetags.extra_filters import indian_currency
#         results['filter_load'] = "✅ extra_filters loaded OK"
#         results['filter_test'] = str(indian_currency(123456.78))
#     except Exception as e:
#         results['filter_load']  = f"❌ FAILED: {e}"
#         results['filter_trace'] = traceback.format_exc()
#         return JsonResponse(results, json_dumps_params={'indent': 2})

#     # ── Step 3: Render template ──
#     try:
#         client = get_object_or_404(QtnClient, id=client_id)
#         rows   = list(QuotationItem.objects.filter(client_id=client_id))

#         subtotal       = sum((getattr(r, 'total', 0) or 0 for r in rows), Decimal("0.00"))
#         gst_rate       = Decimal(str(getattr(client, 'gst', 0) or 0))
#         gst_amount     = (subtotal * gst_rate) / Decimal("100")
#         total_with_gst = subtotal + gst_amount
#         grand_total    = total_with_gst

#         context = {
#             "client":           client,
#             "rows":             rows,
#             "total_amount":     subtotal,
#             "gst_rate":         gst_rate,
#             "gst_amount":       gst_amount,
#             "discount":         Decimal("0.00"),
#             "grand_total":      grand_total,
#             "quotation_number": f"QTN-{client_id}",
#             "total_with_gst":   total_with_gst,
#             "today":            date.today(),
#         }

#         html = get_template("billing/quotation/pdf_print.html").render(context)
#         results['template_render'] = "✅ OK"
#         results['html_length']     = len(html)

#     except Exception as e:
#         results['template_render'] = f"❌ FAILED: {e}"
#         results['template_trace']  = traceback.format_exc()
#         return JsonResponse(results, json_dumps_params={'indent': 2})

#     # ── Step 4: pisa PDF ──
#     try:
#         from xhtml2pdf import pisa
#         buf    = BytesIO()
#         result = pisa.CreatePDF(
#             html,
#             dest=buf,
#             link_callback=fetch_resources,
#             encoding='utf-8'
#         )
#         results['pisa_errors']  = result.err
#         results['pisa_status']  = "✅ OK" if not result.err else f"❌ pisa error: {result.err}"
#         results['pisa_pdf_size'] = buf.tell()
#         buf.seek(0)
#         qtn_bytes = buf.read()

#     except Exception as e:
#         results['pisa_status'] = f"❌ EXCEPTION: {e}"
#         results['pisa_trace']  = traceback.format_exc()
#         return JsonResponse(results, json_dumps_params={'indent': 2})

#     # ── Step 5: Merge ──
#     try:
#         try:
#             from pypdf import PdfMerger
#             results['merger_lib'] = "pypdf"
#         except ImportError:
#             from PyPDF2 import PdfMerger
#             results['merger_lib'] = "PyPDF2"

#         merger = PdfMerger()

#         if results['front_pdf_exists']:
#             merger.append(front_pdf)
#             results['merge_front'] = "✅ Added"
#         else:
#             results['merge_front'] = "⚠️ Skipped"

#         merger.append(BytesIO(qtn_bytes))
#         results['merge_quotation'] = "✅ Added"

#         if results['back_pdf_exists']:
#             merger.append(back_pdf)
#             results['merge_back'] = "✅ Added"
#         else:
#             results['merge_back'] = "⚠️ Skipped"

#         out = BytesIO()
#         merger.write(out)
#         merger.close()
#         out.seek(0)
#         final_bytes = out.read()

#         results['merge_status']   = "✅ OK"
#         results['final_pdf_size'] = len(final_bytes)

#     except Exception as e:
#         results['merge_status'] = f"❌ FAILED: {e}"
#         results['merge_trace']  = traceback.format_exc()

#     results['overall'] = "✅ ALL STEPS PASSED" if all(
#         "✅" in str(v) for k, v in results.items()
#         if k.endswith('_status') or k.endswith('_render') or k.endswith('_load')
#     ) else "❌ SOME STEPS FAILED"

#     return JsonResponse(results, json_dumps_params={'indent': 2})





@login_required
@require_POST
def save_quotation_order(request, client_id):
    """Save the reordered items to database"""
    
    try:
        data = json.loads(request.body)
        order = data.get("order", [])
        
        for index, item_id in enumerate(order):
            QuotationItem.objects.filter(
                id=item_id,
                client_id=client_id
            ).update(sort_order=index)
        
        return JsonResponse({"status": "success"})
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)



@login_required
def save_quotation_totals(request, client_id):

    client = get_object_or_404(QtnClient, id=client_id)

    if request.method == "POST":

        def safe_decimal(val):
            try:
                return Decimal(val)
            except:
                return Decimal("0.00")

        gst_percent = safe_decimal(request.POST.get("gst_percent"))
        discount_value = safe_decimal(request.POST.get("discount_value"))
        discount_type = request.POST.get("discount_type") or "amount"

        # ✅ FIXED GST
        client.gst = gst_percent

        # ✅ FIXED MODEL
        subtotal = sum(
            (r.total for r in QuotationItem.objects.filter(client_id=client_id)),
            Decimal("0.00")
        )

        if discount_type == "percent":
            client.discount_percent = discount_value
            client.discount_amount = (subtotal * discount_value) / Decimal("100")
            client.discount_mode = "percent"
        else:
            client.discount_amount = discount_value
            client.discount_percent = Decimal("0.00")
            client.discount_mode = "amount"

        client.save()

    return redirect("quotation_detail", client_id=client_id)






import os
from django.conf import settings
from urllib.parse import urlparse


def fetch_resources(uri, rel):
    path = urlparse(uri).path

    if path.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, path.replace(settings.MEDIA_URL, ""))

    if path.startswith(settings.STATIC_URL):
        return os.path.join(settings.STATIC_ROOT, path.replace(settings.STATIC_URL, ""))

    return uri


##delete all quotations of a client (with confirmation)
@login_required
def quotation_delete(request, id):

    # id is CLIENT ID
    rows = Quotation.objects.filter(client_id=id)

    if not rows.exists():
        return redirect("quotation_index")

    if request.method == "POST":
        rows.delete()
        return redirect("quotation_index")

    return render(request, "quotation/confirm_delete.html", {
        "client": rows.first().client
    })


###################################################



from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelform_factory
from .models import Image
from django.contrib.auth.decorators import login_required

ImageForm = modelform_factory(Image, fields="__all__")


@login_required
def image_index(request):
    data = Image.objects.all()
    return render(request, "billing/image/index.html", {"data": data})


@login_required
def image_create(request):
    if request.method == 'POST':

        # ===== AJAX (multipart — no json.loads) =====
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                name = request.POST.get('name', '').strip()
                image_file = request.FILES.get('image')

                if not name:
                    return JsonResponse({
                        'success': False,
                        'error': 'Image name is required'
                    }, status=400)

                if not image_file:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please select an image file'
                    }, status=400)

                # Validate type
                allowed_types = [
                    'image/jpeg',
                    'image/png',
                    'image/webp',
                    'image/gif'
                ]
                if image_file.content_type not in allowed_types:
                    return JsonResponse({
                        'success': False,
                        'error': 'Only JPG, PNG, WEBP, GIF allowed'
                    }, status=400)

                # Validate size (5MB)
                if image_file.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'error': 'File too large. Max 5MB allowed'
                    }, status=400)

                img = Image.objects.create(
                    name=name,
                    image=image_file
                )

                return JsonResponse({
                    'success': True,
                    'id': img.id,
                    'name': img.name,
                    'url': img.image.url,
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)

        # ===== Normal POST =====
        name = request.POST.get('name', '').strip()
        image_file = request.FILES.get('image')
        if name and image_file:
            Image.objects.create(name=name, image=image_file)
        return redirect('image_index')

    return render(request, 'billing/image/create.html')




@login_required
def image_update(request, id):
    image = get_object_or_404(Image, id=id)

    if request.method == "POST":

        image.name = request.POST["name"]

        if "image" in request.FILES:
            image.image = request.FILES["image"]

        image.save()
        return redirect("image_index")

    return render(request, "billing/image/update.html", {
        "image": image
    })




@login_required
def image_delete(request, id):
    obj = get_object_or_404(Image, id=id)

    if request.method == "POST":
        obj.delete()
        return redirect("image_index")

    return render(request, "billing/image/confirm_delete.html", {
        "image": obj
    })




# convert all quotations of a client to a spend 

@login_required
def convert_qtn_page(request, client_id):

    items = QuotationItem.objects.filter(client_id=client_id)

    return render(request, "billing/quotation/convert.html", {
        "items": items,
        "clients": Client.objects.all(),
        "projects": Project.objects.all(),
    })




from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

@login_required
def convert_qtn_to_spend(request):

    if request.method == "POST":

        project_id = request.POST.get("project")
        selected_items = request.POST.getlist("items")

        # ✅ VALIDATION
        if not project_id:
            messages.error(request, "Project is required.")
            return redirect(request.META.get('HTTP_REFERER'))

        if not selected_items:
            messages.error(request, "Please select at least one item.")
            return redirect(request.META.get('HTTP_REFERER'))

        # 🔥 BULK FETCH (IMPORTANT)
        items = QuotationItem.objects.select_related('full_semi').filter(id__in=selected_items)

        if not items.exists():
            messages.error(request, "No valid items found.")
            return redirect(request.META.get('HTTP_REFERER'))

        # 🔥 PRELOAD (performance boost)
        floors = {f.name.lower(): f for f in FloorType.objects.all()}
        rooms = list(RoomType.objects.all())

        rows = []

        for item in items:

            # 🔥 FLOOR MATCH (fast dict lookup)
            floor_obj = floors.get(item.floor.lower()) if item.floor else None

            # 🔥 ROOM MATCH (smart reverse match)
            room_obj = None
            if item.location:
                loc = item.location.lower()
                for r in rooms:
                    if r.name.lower() in loc:
                        room_obj = r
                        break

            # 🔥 DESCRIPTION FIX
            desc = (item.specification or "").strip()
            if not desc:
                desc = item.element

            # 🔥 RATE FIX (IMPORTANT 🔥)
            rate = item.price or Decimal("0.00")

            # fallback to fullsemi if price missing
            if rate == 0 and item.full_semi:
                rate = item.full_semi.rate

            # 🔥 CREATE OBJECT
            rows.append(
                Spend(
                    project_id=project_id,

                    floor=floor_obj,
                    room=room_obj,
                    fullsemi=item.full_semi,

                    elements=item.element,
                    description=desc,

                    length=item.length,
                    width=item.width,
                    area=item.area,

                    rate=rate,
                    qty=item.qty or Decimal("1"),
                )
            )

        if rows:
            with transaction.atomic():

                # 🔥 BULK INSERT
                Spend.objects.bulk_create(rows, batch_size=500)

                # 🔥 FAST TOTAL CALCULATION
                total_amount = sum(
                    (r.area or Decimal("0")) * (r.rate or Decimal("0")) * (r.qty or Decimal("0"))
                    for r in rows
                )

                # 🔥 UPDATE PROJECT
                project = Project.objects.select_for_update().get(id=project_id)
                project.budget += total_amount
                project.save(update_fields=["budget"])

            messages.success(request, f"{len(rows)} items converted successfully.")
        else:
            messages.error(request, "No valid items to convert.")

        return redirect("spend_list")



# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
import json

from django.utils.timezone import now
from datetime import timedelta
from django.db import transaction
import time

@login_required
@require_POST
def quotation_draft_save(request):

    try:
        data = json.loads(request.body)
        draft_data = data.get('draft_data', {})
        timestamp = data.get('timestamp')
        quotation_id = draft_data.get('quotation_id')  # 🔥 IMPORTANT

        # 🔥 RUN CLEANUP ONLY OCCASIONALLY (every 10 mins)
        last_cleanup = request.session.get("last_draft_cleanup", 0)
        current_time = time.time()

        if current_time - last_cleanup > 600:  # 10 minutes
            cutoff_time = now() - timedelta(days=1)

            QuotationDraft.objects.filter(
                updated_at__lt=cutoff_time
            ).delete()

            request.session["last_draft_cleanup"] = current_time

        # 🔥 SAVE DRAFT
        quotation_id = draft_data.get('quotation_id')
        
        with transaction.atomic():
            QuotationDraft.objects.update_or_create(
                user=request.user,
                quotation_id=quotation_id,   # ✅ IMPORTANT
                defaults={
                    'data': draft_data,
                    'timestamp': timestamp,
                }
            )

        return JsonResponse({
            'success': True,
            'message': 'Draft saved successfully',
            'timestamp': timestamp
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@login_required
@require_POST
def keep_alive(request):
    """Keep session alive"""
    request.session.modified = True
    return JsonResponse({'success': True})


@ensure_csrf_cookie
@require_GET
def get_csrf_token(request):
    """Return a fresh CSRF token"""
    from django.middleware.csrf import get_token
    token = get_token(request)
    return JsonResponse({'token': token})







from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def profile(request):

    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        user.save()
        messages.success(request, "Profile updated successfully.")

    return render(request, "billing/profile.html", {
        "user_obj": user
    })



from django.shortcuts import render
from django.db.models import Value, CharField, Sum, F, DateTimeField, DecimalField, ExpressionWrapper
from django.db.models.functions import Cast
from datetime import date
from itertools import chain
from operator import attrgetter
from .models import Spend, Payment


def my_activity(request):

    today = date.today()

    spends = (
        Spend.objects.filter(created_at__date=today)
        .select_related("project")
        .annotate(
            activity_type=Value("spend", output_field=CharField()),
            activity_amount=ExpressionWrapper(
                F("area") * F("rate") * F("qty"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )

    payments = (
        Payment.objects.filter(date=today)
        .select_related("project")
        .annotate(
            activity_type=Value("payment", output_field=CharField()),
            created_at=Cast("date", output_field=DateTimeField())
        )
    )

    activity_log = sorted(
        chain(spends, payments),
        key=attrgetter("created_at"),
        reverse=True
    )

    total_spend = spends.aggregate(total=Sum("activity_amount"))["total"] or 0
    total_pay = payments.aggregate(total=Sum("amount"))["total"] or 0

    return render(request, "billing/my_activity.html", {
        "activity_log": activity_log,
        "total_spend_today": total_spend,
        "total_pay_today": total_pay,
    })




import os
import zipfile
import subprocess
from datetime import datetime
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required


# ✅ helper — auto delete old backups
def cleanup_old_backups(days=30):
    backup_dir = os.path.join(settings.BASE_DIR, "backups")

    if not os.path.exists(backup_dir):
        return

    now_ts = datetime.now().timestamp()

    for filename in os.listdir(backup_dir):
        if not filename.lower().endswith(".zip"):
            continue

        file_path = os.path.join(backup_dir, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            file_age_days = (now_ts - os.path.getctime(file_path)) / 86400
            if file_age_days > days:
                os.remove(file_path)
        except Exception:
            pass


@login_required
def download_backup(request):

    # 🔥 AUTO CLEANUP (before creating new backup)
    cleanup_old_backups(days=30)

    db = settings.DATABASES['default']

    DB_NAME = db['NAME']
    DB_USER = db['USER']
    DB_PASSWORD = db['PASSWORD']
    DB_HOST = db.get('HOST') or 'localhost'
    DB_PORT = db.get('PORT') or '3306'

    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    sql_filename = f"backup_{timestamp}.sql"
    zip_filename = f"backup_{timestamp}.zip"

    sql_path = os.path.join(backup_dir, sql_filename)
    zip_path = os.path.join(backup_dir, zip_filename)

    try:
        # ✅ SAFE mysqldump (no shell)
        with open(sql_path, 'w') as outfile:
            result = subprocess.run(
                [
                    "mysqldump",
                    f"-h{DB_HOST}",
                    f"-P{DB_PORT}",
                    f"-u{DB_USER}",
                    f"-p{DB_PASSWORD}",
                    DB_NAME,
                ],
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True,
            )

        if result.returncode != 0:
            return HttpResponse(
                f"Backup failed: {result.stderr}",
                status=500
            )

        # ✅ Create ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sql_path, sql_filename)

        # ✅ remove sql after zip
        if os.path.exists(sql_path):
            os.remove(sql_path)

        return FileResponse(
            open(zip_path, 'rb'),
            as_attachment=True,
            filename=zip_filename
        )

    except FileNotFoundError:
        return HttpResponse(
            "mysqldump not found on server. Please install mysql-client.",
            status=500
        )

    except Exception as e:
        return HttpResponse(
            f"Backup failed: {str(e)}",
            status=500
        )





import os
import zipfile
import subprocess
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def restore_backup(request):

    if request.method == 'POST' and request.FILES.get('backup_file'):

        db = settings.DATABASES['default']

        DB_NAME = db['NAME']
        DB_USER = db['USER']
        DB_PASSWORD = db['PASSWORD']
        DB_HOST = db.get('HOST') or 'localhost'
        DB_PORT = db.get('PORT') or '3306'

        backup_file = request.FILES['backup_file']

        # ✅ validate file type
        if not backup_file.name.endswith('.zip'):
            return HttpResponse("Invalid file. Please upload ZIP backup.", status=400)

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        zip_path = os.path.join(backup_dir, backup_file.name)

        # ✅ save uploaded file
        with open(zip_path, 'wb+') as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        try:
            # ✅ extract zip safely
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(backup_dir)

            # ✅ find latest SQL file from this zip only
            sql_file = None
            for name in zip_ref.namelist():
                if name.endswith('.sql'):
                    sql_file = os.path.join(backup_dir, name)
                    break

            if not sql_file or not os.path.exists(sql_file):
                return HttpResponse("No SQL file found in backup.", status=400)

            # ✅ restore database (SAFE — no shell=True)
            with open(sql_file, 'rb') as infile:
                result = subprocess.run(
                    [
                        "mysql",
                        f"-h{DB_HOST}",
                        f"-P{DB_PORT}",
                        f"-u{DB_USER}",
                        f"-p{DB_PASSWORD}",
                        DB_NAME,
                    ],
                    stdin=infile,
                    stderr=subprocess.PIPE,
                )

            if result.returncode != 0:
                return HttpResponse(
                    f"Restore failed: {result.stderr.decode()}",
                    status=500
                )

            return redirect('dashboard')

        except zipfile.BadZipFile:
            return HttpResponse("Invalid ZIP file.", status=400)

    return render(request, 'billing/backup/restore.html')



import os
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def backup_history(request):

    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    backup_files = []

    try:
        for filename in os.listdir(backup_dir):

            # ✅ only allow zip backups
            if not filename.lower().endswith(".zip"):
                continue

            file_path = os.path.join(backup_dir, filename)

            # skip if not file
            if not os.path.isfile(file_path):
                continue

            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            created_time = os.path.getctime(file_path)

            backup_files.append({
                "name": filename,
                "size": round(size_mb, 2),
                "created": datetime.fromtimestamp(created_time),
                "created_human": datetime.fromtimestamp(created_time).strftime("%d %b %Y, %I:%M %p"),
            })

    except FileNotFoundError:
        backup_files = []

    # ✅ latest first
    backup_files.sort(key=lambda x: x["created"], reverse=True)

    return render(request, "billing/backup/history.html", {
        "backup_files": backup_files
    })




from django.http import FileResponse, Http404


import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.text import get_valid_filename


@login_required
def download_backup_file(request, filename):

    # ✅ sanitize filename
    filename = get_valid_filename(filename)

    # ✅ only allow zip downloads
    if not filename.lower().endswith(".zip"):
        raise Http404("Invalid backup file")

    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    file_path = os.path.join(backup_dir, filename)

    # ✅ prevent path traversal attack
    if not os.path.abspath(file_path).startswith(os.path.abspath(backup_dir)):
        raise Http404("Invalid file path")

    if not os.path.exists(file_path):
        raise Http404("Backup file not found")

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=filename
    )




import os
from django.conf import settings
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.text import get_valid_filename


@login_required
def delete_backup_file(request, filename):

    # ✅ sanitize filename
    filename = get_valid_filename(filename)

    if not filename.lower().endswith(".zip"):
        raise Http404("Invalid file")

    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    file_path = os.path.join(backup_dir, filename)

    # ✅ prevent path traversal
    if not os.path.abspath(file_path).startswith(os.path.abspath(backup_dir)):
        raise Http404("Invalid path")

    if not os.path.exists(file_path):
        raise Http404("File not found")

    # ✅ delete file
    os.remove(file_path)

    messages.success(request, "Backup deleted successfully.")

    return redirect("backup_history")




from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def admin_password_change(request):
    return redirect('/admin/password_change/')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def help_page(request):

    roadmap = [
        {
            "title": "Client Creation",
            "icon": "bi-people",
            "steps": [
                "Go to Clients → Add New Client",
                "Enter name, phone, email",
                "Add GST & discount details",
                "Save client profile"
            ]
        },
        {
            "title": "Project Creation",
            "icon": "bi-kanban",
            "steps": [
                "Open client → Create Project",
                "Enter project name & budget",
                "Set project status",
                "Save project"
            ]
        },
        {
            "title": "Add Expenses (Spends)",
            "icon": "bi-receipt",
            "steps": [
                "Go to project",
                "Add floor, room, material",
                "Enter qty & rate",
                "System auto calculates total"
            ]
        },
        {
            "title": "Quotation System",
            "icon": "bi-file-earmark-text",
            "steps": [
                "Create quotation client",
                "Add items (floor, location, element)",
                "Set GST & discount",
                "Preview and reorder rows",
                "Download PDF"
            ]
        },
        {
            "title": "Payments & Invoice",
            "icon": "bi-wallet2",
            "steps": [
                "Add payment for project",
                "System tracks paid vs remaining",
                "Generate invoice",
                "Share via WhatsApp link"
            ]
        },
        {
            "title": "Public Invoice Sharing",
            "icon": "bi-link-45deg",
            "steps": [
                "Click share invoice",
                "Send link to client",
                "Client views without login"
            ]
        }
    ]

    return render(request, "billing/help.html", {
        "roadmap": roadmap
    })