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

@login_required(login_url='login')
def dashboard(request):


    # 🔢 Totals
    spends = Spend.objects.all()
    total_clients = Client.objects.count()
    total_projects = Project.objects.count()

    total_payments = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or Decimal("0.00")

    total_spend = sum(
        (spend.total_amount for spend in spends),
        Decimal("0.00")
    )

    # 🆕 Recent Data
    recent_clients = Client.objects.order_by('-created_at')[:5]

    recent_payments = Payment.objects.select_related(
        'project__client'
    ).order_by('-date', '-id')[:5]

    recent_spends = Spend.objects.select_related(
        'project'
    ).order_by('-id')[:5]

    # 📂 All projects (for table if needed)
    projects = Project.objects.select_related('client')

    context = {
        'total_clients': total_clients,
        'total_projects': total_projects,
        'total_payments': total_payments,
        'total_spend': total_spend,
        'recent_clients': recent_clients,
        'recent_payments': recent_payments,
        'recent_spends': recent_spends,
        'projects': projects,
    }

    return render(request, 'billing/dashboard.html', context)



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
                F('qty') * F('rate'),
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

    query = request.GET.get('q')

    spends = (
        Spend.objects
        .select_related('project__client', 'floor', 'room', 'fullsemi')
        .order_by('-id')
    )

    # 🔍 Apply Search Filter
    if query:
        spends = spends.filter(
            Q(project__name__icontains=query) |
            Q(project__client__name__icontains=query) 
            # Q(floor__name__icontains=query) |
            # Q(room__name__icontains=query) |
            # Q(elements__icontains=query) |
            # Q(description__icontains=query) |
            # Q(rate__icontains=query)
        )

    return render(request, 'billing/spend/index.html', {
        'spends': spends,
        'query': query,
    })



# 📌 Spend Create
def spend_create(request):

    projects = Project.objects.select_related('client').all()
    floors = FloorType.objects.all()
    rooms = RoomType.objects.all()
    fullsemis = FullSemi.objects.all()

    if request.method == 'POST':

        try:
            length = request.POST.get('length')
            width = request.POST.get('width')
            qty = request.POST.get('qty') or "1"

            length = Decimal(length) if length else None
            width = Decimal(width) if width else None
            qty = Decimal(qty)

        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid numeric input.")
            return redirect('spend_create')

        unit = request.POST.get('unit') or "sqft"

        spend = Spend.objects.create(
            project_id=request.POST.get('project') or None,
            floor_id=request.POST.get('floor') or None,
            room_id=request.POST.get('room') or None,
            fullsemi_id=request.POST.get('fullsemi') or None,   # ✅ FIXED
            elements=request.POST.get('elements'),              # ✅ NEW FIELD
            description=request.POST.get('description'),
            length=length,
            width=width,
            unit=unit,
            qty=qty,
        )

        spend.refresh_from_db()

        # 🔥 Update project budget
        project = spend.project
        project.budget += spend.total_amount
        project.save()

        messages.success(request, "Spend entry created successfully.")
        return redirect('spend_list')

    return render(request, 'billing/spend/create.html', {
        'projects': projects,
        'floors': floors,
        'rooms': rooms,
        'fullsemis': fullsemis,  # renamed
    })




# 📌 Spend Update
def spend_update(request, pk):

    spend = get_object_or_404(Spend, pk=pk)

    projects = Project.objects.select_related('client').all()
    floors = FloorType.objects.all()
    rooms = RoomType.objects.all()
    fullsemis = FullSemi.objects.all()

    if request.method == 'POST':

        old_project = spend.project
        old_total = spend.total_amount

        try:
            length = request.POST.get('length')
            width = request.POST.get('width')
            qty = request.POST.get('qty') or "1"

            spend.length = Decimal(length) if length else None
            spend.width = Decimal(width) if width else None
            spend.qty = Decimal(qty)

        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid numeric input.")
            return redirect('spend_update', pk=pk)

        spend.project_id = request.POST.get('project') or None
        spend.floor_id = request.POST.get('floor') or None
        spend.room_id = request.POST.get('room') or None
        spend.fullsemi_id = request.POST.get('fullsemi') or None   # ✅ FIXED
        spend.elements = request.POST.get('elements')              # ✅ NEW FIELD
        spend.description = request.POST.get('description')
        spend.unit = request.POST.get('unit') or "sqft"

        spend.save()

        new_total = spend.total_amount
        new_project = spend.project

        # 🔥 Correct budget adjustment
        if old_project == new_project:
            difference = new_total - old_total
            new_project.budget += difference
            new_project.save()
        else:
            old_project.budget -= old_total
            old_project.save()

            new_project.budget += new_total
            new_project.save()

        messages.success(request, "Spend updated successfully.")
        return redirect('spend_list')

    return render(request, 'billing/spend/update.html', {
        'spend': spend,
        'projects': projects,
        'floors': floors,
        'rooms': rooms,
        'fullsemis': fullsemis,   # renamed
    })



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






# 📌 Payment List
def payment_list(request):

    query = request.GET.get('q')

    payments = Payment.objects.select_related(
        'project__client'
    ).order_by('-id')

    # 🔍 Apply Search Filter
    if query:
        payments = payments.filter(
            Q(project__name__icontains=query) |
            Q(project__client__name__icontains=query) |
            Q(payment_mode__icontains=query) |
            Q(amount__icontains=query)
        )

    context = {
        'payments': payments,
        'query': query,
    }

    return render(request, 'billing/payment/index.html', context)


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


# 📌 Payment Update
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    projects = Project.objects.all()

    if request.method == 'POST':
        payment.project_id = request.POST.get('project')
        payment.amount = request.POST.get('amount')
        payment.payment_mode = request.POST.get('payment_mode')
        payment.save()
        return redirect('payment_list')

    return render(request, 'billing/payment/update.html', {
        'payment': payment,
        'projects': projects,
    })


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

    if client.gst_number:
        gst_rate = Decimal("18.00")
    else:
        gst_rate = Decimal("0.00")

    gst_amount = (total_spent * gst_rate) / Decimal("100")

    # Discount from client
    discount = client.discount or Decimal("0.00")


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
    return render(request, 'billing/payment/invoice.html', context)


def public_invoice(request, token):

    payment = get_object_or_404(
        Payment.objects.select_related('project__client'),
        invoice_token=token
    )

    context = build_invoice_context(request, payment)
    return render(request, 'billing/payment/invoice.html', context)


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
