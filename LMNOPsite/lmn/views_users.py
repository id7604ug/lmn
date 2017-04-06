from django.shortcuts import render, redirect

from .models import Venue, Artist, Note, Show
from .forms import VenueSearchForm, NoteForm, ArtistSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone



def user_profile(request, user_pk):
    user = User.objects.get(pk=user_pk)
    usernotes = Note.objects.filter(user=user.pk).order_by('posted_date').reverse()
    return render(request, 'lmn/users/user_profile.html', {'user' : user , 'notes' : usernotes })



@login_required
def my_user_profile(request):
    # TODO - editable version for logged-in user to edit own profile
    return redirect('lmn:user_profile', user_pk=request.user.pk)



def register(request):

    if request.method == 'POST':

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect('lmn:homepage')

        else :
            message = 'Please check the data you entered'
            return render(request, 'registration/register.html', { 'form' : form , 'message' : message } )


    else:
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', { 'form' : form } )
