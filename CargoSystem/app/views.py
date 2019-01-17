from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.urlresolvers import reverse
from app.models import IsikCargos
from .forms import AddCargoForm
from .forms import LoginForm
from django.contrib import messages
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import (
    get_user_model,
    authenticate,
    login as auth_login,
    logout as auth_logout,
)

from django.views.generic import (
    CreateView
)
from .forms import (
    UserCreateForm,
)

User = get_user_model()

def login(request):
    User = get_user_model()
    if request.method=='POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            print(username,password)
            if user is not None:
                auth_login(request, user)
                if user.user_type == 'customer':
                    return redirect('cargo_list')
                elif user.user_type == 'manager':
                    return redirect('cargo_center_list')
                elif user.user_type == 'transporter':
                    return redirect('cargos_list')
            else:
                messages.info(request, 'wrong password or username.')
                return render(request, 'app/Login.html', {})
    else:
        return render(request, 'app/Login.html', {})


@login_required(login_url='login')
def cargo_list(request):
    if request.user.user_type=='customer':
        qs = IsikCargos.objects.filter(to_who__tc_no=request.user.tc_no)
        context = {}
        print("cargolist")
        if qs is not None:
            context['cargos'] = qs
        return render(request, 'app/cargos_list.html', context)
    else :
        qs = IsikCargos.objects.all()
        if qs is not None:
            context = {}
            context['cargos'] = qs
        return render(request, 'app/cargos_list.html', context)

@login_required(login_url='login')
def cargos_list(request):
    qs = IsikCargos.objects.all()
    print("cargossslist")
    context={}
    if qs is not None:
        context= {'cargos':qs}

    return render(request, 'app/cargos_list.html', context)

@login_required(login_url='login')
def cargo_center_list(request):
    qs = IsikCargos.objects.all()
    context = {'cargos': qs}

    if request.method == 'POST':
        form = AddCargoForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['from_who']
            tc_no = form.cleaned_data['to_who']
            user_qs = User.objects.filter(tc_no=tc_no)
            if user_qs.exists():
                user = user_qs.first()
                obj = IsikCargos(to_who=user, from_who=source)
                obj.save()
                return HttpResponseRedirect(request.path_info)
            return redirect(request.path_info)
    else:
        form = AddCargoForm()

    context['form'] = form
    return render(request,'app/cargos_admin.html',context)

@login_required(login_url='login')
def cargo_detail(request, pk=None):
    cargo = IsikCargos.objects.get(pk=pk)
    if request.method=='POST':
        take_cargo(request,pk)
        return cargo_list(request);
    return render(request, 'app/cargo_detail.html', {'cargo': cargo})

@login_required(login_url='login')
def logout_view(request):
    if request.method=='POST':
        auth_logout(request)
        return redirect('login')

class RegisterView(CreateView):
    template_name = 'app/register.html'
    form_class = UserCreateForm

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, 'app/register.html', context)

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        if valid:
            user = form.instance
            username = self.request.POST.get("username").strip()
            password = self.request.POST.get("password")
            user = authenticate(username=username, password=password)
            auth_login(self.request, user)
        return valid

    def get_success_url(self):
        return reverse('login')

@login_required(login_url='login')
def take_cargo(request,pk=None):
     print("take cargo")
     if request.method =='POST':
        time=datetime.today()
        name=request.user
        cargo = IsikCargos.objects.get(pk=pk)
        cargo.who_has_now=name
        cargo.taken_cargo_date=time
        cargo.save()
        mail_for_customer=cargo.to_who
        find_user=User.objects.get(username=mail_for_customer)
        find_user_mail=find_user.email
        subject = "about your cargo"
        from_email = settings.EMAIL_HOST_USER
        send_message = find_user.username+" took your cargos "

        send_mail(subject=subject,
                 from_email=from_email,
                 recipient_list=[find_user_mail],
                 message=send_message,
                 fail_silently=False)

        return redirect(request.path_info)