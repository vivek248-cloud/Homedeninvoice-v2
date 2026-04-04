from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
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

# client login


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Client, Project



from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from .models import Client

CLIENT_FIXED_PASSWORD = "homeden@2025"


@require_http_methods(["GET", "POST"])
def client_login(request):

    if request.session.get("client_id"):
        return redirect("client_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 🔥 use filter instead of get
        client = Client.objects.filter(mobile_1=username).first()

        if not client:
            messages.error(request, "Mobile number not registered")
            return render(request, "billing/client_auth/login.html")

        if password == "homeden@2025":
            request.session["client_id"] = client.id
            return redirect("client_dashboard")
        else:
            messages.error(request, "Invalid password")

    return render(request, "billing/client_auth/login.html")



def client_logout(request):
    request.session.pop("client_id", None)
    return redirect("login")


from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Sum
from decimal import Decimal

def client_dashboard(request):

    client_id = request.session.get("client_id")

    if not client_id:
        return redirect("client_login")

    client = get_object_or_404(Client, id=client_id)

    projects = Project.objects.filter(client=client)

    latest_project = projects.order_by('-id').first()
    project_status = latest_project.status if latest_project else None

    # ✅ CORRECT
    completed_projects = projects.filter(status="Completed").exists()

    payments = (
        Payment.objects
        .filter(project__client=client)
        .select_related("project")
        .order_by("-date")
    )

    total_paid = payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    total_budget = projects.aggregate(
        total=Sum("budget")
    )["total"] or Decimal("0.00")

    total_receivable = total_budget - total_paid

    return render(request, "billing/client_auth/dashboard.html", {
        "client": client,
        "projects": projects,
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
def project_list(request):

    query = request.GET.get('q')

    projects = Project.objects.select_related('client').order_by('-id')

    # 🔍 Apply filter
    if query:
        projects = projects.filter(
            Q(name__icontains=query) |
            Q(client__name__icontains=query)
        )

    # 🔥 Calculate total receivable AFTER filtering
    total_receivable = Decimal("0.00")
    for project in projects:
        total_receivable += project.yet_to_receive

    context = {
        'projects': projects,
        'total_receivable': total_receivable,
        'query': query,
    }

    return render(request, 'billing/project/index.html', context)



# 📌 Project Create
def project_create(request):
    clients = Client.objects.all()

    if request.method == 'POST':
        Project.objects.create(
            client_id=request.POST.get('client'),
            name=request.POST.get('name'),
            budget=request.POST.get('budget'),
            status=request.POST.get('status'),
        )
        return redirect('project_list')

    return render(request, 'billing/project/create.html', {'clients': clients})


# 📌 Project Update
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    clients = Client.objects.all()

    if request.method == 'POST':
        project.client_id = request.POST.get('client')
        project.name = request.POST.get('name')
        project.budget = request.POST.get('budget')
        project.status = request.POST.get('status')
        project.save()

        return redirect('project_list')

    return render(request, 'billing/project/update.html', {
        'project': project,
        'clients': clients
    })


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
def floor_create(request):
    if request.method == 'POST':
        FloorType.objects.create(
            name=request.POST.get('name')
        )
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
def room_create(request):
    if request.method == 'POST':
        RoomType.objects.create(
            name=request.POST.get('name')
        )
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
def fullsemi_create(request):
    if request.method == 'POST':
        FullSemi.objects.create(
            name=request.POST.get('name'),
            rate=request.POST.get('rate')
        )
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





# 📌 Spend List
def spend_list(request):
    client_id = request.GET.get('client')

    spends = Spend.objects.none()

    if client_id:
        spends = (
            Spend.objects
            .select_related('project__client', 'floor', 'room', 'fullsemi')
            .filter(project__client_id=client_id)
            .order_by('-id')
        )

    clients = Client.objects.all()

    return render(request, 'billing/spend/index.html', {
        'spends': spends,
        'clients': clients,
        'selected_client': client_id,
    })



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




from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render


from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from datetime import datetime
import re
from django.urls import reverse
import urllib.parse



def build_invoice_context(request, payment):

    project = payment.project
    client = project.client

    invoice_number = f"INV-{client.id}{payment.id}{payment.date.strftime('%d%m%Y')}"

    client_name = re.sub(r'[^A-Za-z0-9]+', '', client.name.upper())
    project_code = f"{project.id}"
    date_str = payment.date.strftime('%d-%m-%Y')
    invoice_filename = f"{client_name}-{project_code}-{date_str}"

    invoice_url = request.build_absolute_uri(
        reverse('public_invoice', args=[payment.invoice_token])
    )

    spends = project.spends.select_related(
        'floor', 'room', 'fullsemi'
    ).order_by(
        'floor__name',
        'room__name',
        'id'
    )

    total_spent = project.total_spent
    # GST based on client GST registration

    # ✅ Use saved values if exist, else defaults
    gst_rate = payment.gst_rate or (
        Decimal("0.00") if client.gst_number else Decimal("0.00")
    )

    gst_amount = (total_spent * gst_rate) / Decimal("100")

    discount_value = payment.discount_value or Decimal("0.00")
    discount_type = payment.discount_type or "percent"

    if discount_type == "percent":
        discount = (total_spent + gst_amount) * discount_value / Decimal("100")
    else:
        discount = discount_value

    grand_total = total_spent + gst_amount - discount

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


    payment_rows = []
    running_total = Decimal("0.00")

    for p in payments:

        if not p.invoice_token:
            p.invoice_token = uuid.uuid4()
            p.save(update_fields=['invoice_token'])

        previous_paid = running_total
        running_total += p.amount

        payment_rows.append({
            'token': p.invoice_token,
            'id': p.id,
            'date': p.date,
            'previous_paid': previous_paid,
            'now_paid': p.amount,
            'total_paid': running_total,
            'balance_after': grand_total - running_total,
            'mode': p.get_payment_mode_display(),
        })


    return {
        'project': project,
        'payment': payment,
        'spends': spends,
        'total_spent': total_spent,
        'gst_rate': gst_rate,
        'gst_amount': gst_amount,
        'discount': discount,
        'grand_total': grand_total,
        'payment_rows': payment_rows,
        'invoice_number': invoice_number,
        'invoice_filename': invoice_filename,
        'invoice_url': invoice_url,
        'whatsapp_url': whatsapp_url,
    }


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




@login_required
def qtn_client_create(request):

    if request.method == "POST":

        QtnClient.objects.create(
            name=request.POST.get("name"),
            phone1=request.POST.get("phone1"),
            phone2=request.POST.get("phone2"),
            email=request.POST.get("email"),
            location=request.POST.get("location"),

            gst=request.POST.get("gst"),

            discount_percent=request.POST.get("discount_percent") or 0,
            discount_amount=request.POST.get("discount_amount") or 0,
            discount_mode=request.POST.get("discount_mode") or "percent",

            notes=request.POST.get("notes"),

            estimate_start_date=request.POST.get("estimate_start_date"),
            estimate_end_date=request.POST.get("estimate_end_date"),
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
        return redirect("quotation_index")

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


@login_required
def quotation_create(request):

    if request.method == "POST":

        client_id = request.POST.get("client")

        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        # update quotation client dates
        QtnClient.objects.filter(id=client_id).update(
            estimate_start_date=start_date,
            estimate_end_date=end_date,
        )

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

        quotation_rows = []

        for i in range(len(elements)):

            if not elements[i]:
                continue

            length = Decimal(lengths[i] or 0)
            width = Decimal(widths[i] or 0)
            qty = int(qtys[i] or 1)

            area = length * width

            price = Decimal("0.00")
            fullsemi_id = fullsemis[i] if i < len(fullsemis) else None

            if fullsemi_id:
                try:
                    fullsemi = FullSemi.objects.get(id=fullsemi_id)
                    price = fullsemi.rate
                except FullSemi.DoesNotExist:
                    price = Decimal("0.00")

            # Correct checkbox reading
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

                    unit=units[i] if i < len(units) else "",

                    length=length,
                    width=width,
                    area=area,

                    price=price,
                    qty=qty,
                    total=total,
                    end=end_floor,
                )
            )

        if quotation_rows:
            QuotationItem.objects.bulk_create(quotation_rows)

        return redirect("quotation_index")

    return render(request, "billing/quotation/create.html", {
        "clients": QtnClient.objects.all(),
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
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


@login_required
def quotation_update(request, id):

    rows = QuotationItem.objects.filter(client_id=id)

    if not rows.exists():
        return redirect("quotation_index")

    client_id = id

    if request.method == "POST":

        start_date = request.POST.get("estimate_start_date")
        end_date = request.POST.get("estimate_end_date")

        # update quotation client dates
        QtnClient.objects.filter(id=client_id).update(
            estimate_start_date=start_date,
            estimate_end_date=end_date,
        )

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
        floor_ends = request.POST.getlist("floor_end[]")
        quotation_rows = []

        # preload rates (fast)
        fullsemi_rates = {f.id: f.rate for f in FullSemi.objects.all()}

        for i in range(len(elements)):

            if not elements[i]:
                continue

            length = Decimal(lengths[i] or 0)
            width = Decimal(widths[i] or 0)
            qty = int(qtys[i] or 1)

            area = length * width

            fullsemi_id = fullsemis[i] if i < len(fullsemis) else None
            price = Decimal("0.00")

            if fullsemi_id:
                price = fullsemi_rates.get(int(fullsemi_id), Decimal("0.00"))

            # Correct checkbox reading
            end_floor = request.POST.get(f"floor_end_{i}") == "1"

            total = area * price * qty

            quotation_rows.append(
                QuotationItem(
                    client_id=client_id,

                    floor=floors[i].strip() if i < len(floors) else "",
                    location=locations[i].strip() if i < len(locations) else "",
                    element=elements[i].strip(),

                    image_id=int(images[i]) if i < len(images) and images[i] else None,
                    full_semi_id=fullsemi_id,

                    core_material=core_materials[i] if i < len(core_materials) else "",
                    finish_material=finish_materials[i] if i < len(finish_materials) else "",
                    brand=brands[i] if i < len(brands) else "",
                    specification=specifications[i] if i < len(specifications) else "",

                    unit=units[i] if i < len(units) else "",

                    length=length,
                    width=width,
                    area=area,

                    price=price,
                    qty=qty,
                    total=total,
                    end=end_floor,
                )
            )

        # replace old quotation rows safely
        with transaction.atomic():
            rows.delete()
            if quotation_rows:
                QuotationItem.objects.bulk_create(quotation_rows)

        return redirect("quotation_index")

    return render(request, "billing/quotation/update.html", {
        "quotation_rows": rows,
        "clients": QtnClient.objects.all(),
        "images": Image.objects.all(),
        "fullsemis": FullSemi.objects.all(),
        "previous_specs": list(
            QuotationItem.objects
            .exclude(specification="")
            .values_list("specification", flat=True)
            .distinct()[:200]
        )
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


@login_required
def quotation_detail(request, client_id):

    rows = (
        QuotationItem.objects
        .select_related("client", "image", "full_semi")
        .filter(client_id=client_id)
    )

    if not rows.exists():
        return redirect("quotation_index")

    client = rows.first().client

    # -------------------------
    # Subtotal
    # -------------------------
    subtotal = sum((r.total for r in rows), Decimal("0.00"))

    # -------------------------
    # GST
    # -------------------------
    gst_rate = Decimal(client.gst or 0)
    gst_amount = (subtotal * gst_rate) / Decimal("100")

    total_with_gst = subtotal + gst_amount

    # -------------------------
    # Discount Handling
    # -------------------------
    discount_amount = Decimal("0.00")
    discount_percent = Decimal("0.00")
    discount_mode = client.discount_mode or "amount"

    if discount_mode == "percent":

        discount_percent = Decimal(client.discount_percent or 0)
        discount_amount = (subtotal * discount_percent) / Decimal("100")

    else:

        discount_amount = Decimal(client.discount_amount or 0)

        if subtotal > 0:
            discount_percent = (discount_amount / subtotal) * Decimal("100")

    # -------------------------
    # Final Total
    # -------------------------
    grand_total = max(
        total_with_gst - discount_amount,
        Decimal("0.00")
    )

    return render(
        request,
        "billing/quotation/detail.html",
        {
            "client": client,
            "rows": rows,

            "subtotal": round(subtotal, 2),
            "gst_rate": gst_rate,
            "gst_amount": round(gst_amount, 2),

            "discount_amount": round(discount_amount, 2),
            "discount_percent": round(discount_percent, 2),
            "discount_mode": discount_mode,

            "grand_total": round(grand_total, 2),
        }
    )









@login_required
def quotation_preview(request, client_id):

    client = get_object_or_404(QtnClient, id=client_id)

    rows = QuotationItem.objects.filter(
        client_id=client_id
    ).order_by("id")

    subtotal = sum(r.total for r in rows)

    gst_rate = Decimal(client.gst or 0)
    gst_amount = (subtotal * gst_rate) / Decimal("100")

    total_with_gst = subtotal + gst_amount

    discount = client.discount_amount or Decimal("0.00")

    grand_total = total_with_gst - discount

    return render(
        request,
        "billing/quotation/pdf.html",
        {
            "client": client,
            "rows": rows,
            "subtotal": subtotal,
            "gst_rate": gst_rate,
            "gst_amount": gst_amount,
            "grand_total": grand_total,
            "preview": True
        }
    )



import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def save_quotation_order(request, client_id):

    try:
        data = json.loads(request.body.decode("utf-8"))

        order = data.get("order", [])

        for index, item_id in enumerate(order):

            QuotationItem.objects.filter(
                id=int(item_id),
                client_id=client_id
            ).update(sort_order=index)

        return JsonResponse({
            "status": "success",
            "message": "Order saved"
        })

    except Exception as e:

        print("ORDER SAVE ERROR:", e)   # ← IMPORTANT DEBUG

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)



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



# @login_required
# def quotation_pdf(request, client_id):

#     client = QtnClient.objects.get(id=client_id)

#     rows = (
#         QuotationItem.objects
#         .filter(client_id=client_id)
#         .annotate(
#             floor_lower=Lower("floor"),
#             location_lower=Lower("location"),
#             end_priority=Case(
#                 When(element__iexact="FLASE CEILING - PLAIN", then=Value(1)),
#                 When(element__iexact="ELECTRICAL LABOUR", then=Value(1)),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         )
#         .order_by("floor_lower", "location_lower", "end_priority", "id")
#     )

#     # -------------------------
#     # Subtotal
#     # -------------------------
#     subtotal = sum((r.total for r in rows), Decimal("0.00"))

#     gst_rate = Decimal(client.gst or 0)
#     gst_amount = (subtotal * gst_rate) / Decimal("100")

#     total_with_gst = subtotal + gst_amount

#     # Discount
#     if client.discount_mode == "percent":
#         percent = Decimal(client.discount_percent or 0)
#         discount_amount = (subtotal * percent) / Decimal("100")
#     else:
#         discount_amount = Decimal(client.discount_amount or 0)

#     grand_total = max(
#         total_with_gst - discount_amount,
#         Decimal("0.00")
#     )

#     quotation_number = f"QTN-{client.id}-{date.today().strftime('%m%y')}"

#     # Render HTML
#     template = get_template("billing/quotation/pdf.html")

#     html = template.render({
#         "client": client,
#         "rows": rows,

#         "total_amount": subtotal,
#         "gst_rate": gst_rate,
#         "gst_amount": gst_amount,

#         "discount": discount_amount,
#         "grand_total": grand_total,

#         "quotation_number": quotation_number,
#         "total_with_gst": total_with_gst,
#         "today": date.today(),
#     })

#     quotation_buffer = BytesIO()

#     pisa_status = pisa.CreatePDF(
#         html,
#         dest=quotation_buffer,
#         link_callback=fetch_resources
#     )

#     if pisa_status.err:
#         return HttpResponse("PDF generation error", status=500)

#     quotation_buffer.seek(0)

#     # Static PDFs
#     front_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "front.pdf")
#     back_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "back.pdf")

#     merger = PdfMerger()

#     if os.path.exists(front_pdf):
#         merger.append(front_pdf)

#     merger.append(quotation_buffer)

#     if os.path.exists(back_pdf):
#         merger.append(back_pdf)

#     final_buffer = BytesIO()

#     merger.write(final_buffer)
#     merger.close()

#     final_buffer.seek(0)

#     response = HttpResponse(
#         final_buffer.read(),
#         content_type="application/pdf"
#     )

#     response["Content-Disposition"] = (
#         f'inline; filename="QTN_{client.name}_{date.today().strftime("%Y%m%d")}.pdf"'
#     )

#     return response

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


@login_required
def quotation_pdf(request, client_id):

    client = get_object_or_404(QtnClient, id=client_id)

    # -------------------------
    # Get rows
    # -------------------------
    rows = (
        QuotationItem.objects
        .filter(client_id=client_id)
        .annotate(
            floor_lower=Lower("floor"),
            location_lower=Lower("location"),

            # if any row of floor has end=True → whole floor becomes end
            floor_end=Max("end")
        )
        .order_by(
            "floor_end",      # normal floors first
            "floor_lower",
            "location_lower",
            "sort_order",
            "id"
        )
    )

    # -------------------------
    # Totals
    # -------------------------
    subtotal = sum((r.total for r in rows), Decimal("0.00"))

    gst_rate = Decimal(client.gst or 0)
    gst_amount = (subtotal * gst_rate) / Decimal("100")

    total_with_gst = subtotal + gst_amount

    # Discount
    if client.discount_mode == "percent":
        percent = Decimal(client.discount_percent or 0)
        discount_amount = (subtotal * percent) / Decimal("100")
    else:
        discount_amount = Decimal(client.discount_amount or 0)

    grand_total = max(
        total_with_gst - discount_amount,
        Decimal("0.00")
    )

    quotation_number = f"QTN-{client.id}-{date.today().strftime('%m%y')}"

    context = {
        "client": client,
        "rows": rows,
        "total_amount": subtotal,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "discount": discount_amount,
        "grand_total": grand_total,
        "quotation_number": quotation_number,
        "total_with_gst": total_with_gst,
        "today": date.today(),
    }

    # -------------------------
    # PREVIEW MODE
    # -------------------------
    if request.GET.get("preview") == "1":
        return render(request, "billing/quotation/pdf.html", context)

    # -------------------------
    # PDF GENERATION
    # -------------------------
    template = get_template("billing/quotation/pdf.html")
    html = template.render(context)

    quotation_buffer = BytesIO()

    pisa_status = pisa.CreatePDF(
        html,
        dest=quotation_buffer,
        link_callback=fetch_resources
    )

    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)

    quotation_buffer.seek(0)

    # -------------------------
    # Merge with front/back PDFs
    # -------------------------
    front_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "front.pdf")
    back_pdf = os.path.join(settings.MEDIA_ROOT, "pdfs", "back.pdf")

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

    response = HttpResponse(
        final_buffer.read(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="QTN_{client.name}_{date.today().strftime("%Y%m%d")}.pdf"'
    )

    return response


@login_required
def save_quotation_totals(request, client_id):

    client = get_object_or_404(QtnClient, id=client_id)

    if request.method == "POST":

        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0

        gst_percent = safe_float(request.POST.get("gst_percent"))
        discount_value = safe_float(request.POST.get("discount_value"))
        discount_type = request.POST.get("discount_type") or "amount"

        # Save GST
        client.GST = gst_percent

        subtotal = sum(
            r.total for r in Quotation.objects.filter(client_id=client_id)
        )

        # Save discount correctly
        if discount_type == "percent":

            client.discount_percent = discount_value
            client.discount_amount = round(subtotal * discount_value / 100, 2)

            client.discount_mode = "percent"

        else:

            client.discount_amount = discount_value
            client.discount_percent = 0

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
    if request.method == "POST":
        Image.objects.create(
            name=request.POST["name"],
            image=request.FILES["image"]
        )
        return redirect("image_index")

    return render(request, "billing/image/create.html")


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