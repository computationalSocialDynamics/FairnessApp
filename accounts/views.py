from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from accounts.algorithms import Game
from accounts.forms import RegistrationForm, DocumentForm
from accounts.models import UserValues, Robots
from accounts.static.images.imageTexts import getImageTexts, getNames, getSettings, getFlickrIds

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('/accounts/profile')
    args = {'form':form}
    return render(request, 'accounts/reg_form.html', args)

def pages(request):
    if request.user.is_authenticated:
        imageId = request.session['image_id']
        names = getNames()
        imageTexts = getImageTexts()
        settings = getSettings()
        if request.POST:
            user = UserValues.objects.get(user=request.user)
            if 'next' in request.POST:
                request.session['image_id'] += 1
                imageId = request.session['image_id']
                if(imageId >= len(getImageTexts())):
                    return render(request, 'accounts/finished.html', {'imageId':imageId})

            if imageId % 2 == 1:
                preference=""
                change = ""
                if 'began' in request.POST:
                    user.firstLogin = False
                    user.save()

                if 'began' in request.POST or 'next' in request.POST or 'continue' in request.POST:
                    uservalues, current_robot = Game.getRobot(request, 1)
                    robot_offeror_value = list(map(float, current_robot.offeror_values.split()))[-1]
                    request.session['robot_offeror_value'] = robot_offeror_value
                    request.session['current_robot'] = current_robot.id

                if 'preference' in request.POST:
                    preference = request.POST.get('preference')
                    current_robot = Robots.objects.get(id=request.session['current_robot'])
                    (user, robot) = Game.imagePreference(request, current_robot, 1)
                    user_acceptor_values = list(map(float, user.user_acceptor_values.split()))
                    user_offeror_values = list(map(float, user.user_offeror_values.split()))
                    user_acceptor_values.append(user_acceptor_values[-1])
                    user_offeror_values.append(user_offeror_values[-1])
                    '''if ('Yes' in request.POST.get('preference') and request.session['success'] == True) or ('No' in request.POST.get('preference') and request.session['failure'] == True):
                        preference = 'Yes'
                    elif ('No' in request.POST.get('preference') and request.session['success']) or ('Yes' in request.POST.get('preference') and request.session['failure']):
                        preference = 'No'''''
                    user.user_acceptor_values = " ".join(map(str, user_acceptor_values))
                    user.user_offeror_values = " ".join(map(str, user_offeror_values))
                    user.save()
                    robot.save()

                if 'change' in request.POST:
                    change = 'Yes'
                    user_acceptor_values = list(map(float, user.user_acceptor_values.split()))
                    user_offeror_values = list(map(float, user.user_offeror_values.split()))
                    del user_acceptor_values[-1]
                    user_acceptor_values.append(float(request.POST.get('change')))
                    user_offeror_values.append(float(user_offeror_values[-1]))
                    user.user_acceptor_values = " ".join(map(str, user_acceptor_values))
                    user.user_offeror_values = " ".join(map(str, user_offeror_values))
                    user.save()

                settings = getSettings()
                imagePath = "images/" + str(imageId) + ".png"
                args = {'image_id':imageId, 'imagePath': imagePath, 'preference':preference,
                        'change':change, 'text':imageTexts[str(imageId)],
                        'name': names[int(imageId-1)], 'setting': settings[request.session['robot_offeror_value']]}

                return render(request, 'accounts/pages.html', args)
            else:
                form = DocumentForm(request.POST or None)

                if 'began' in request.POST:
                    user = UserValues.objects.get(user=request.user)
                    user.firstLogin = False
                    user.save()

                if 'began' in request.POST or 'next' in request.POST or 'continue' in request.POST:
                    current_robot, uservalues = Game.getRobot(request, 0)
                    request.session['current_robot'] = current_robot.id
                    form = DocumentForm()
                    offeror_val = list(map(float, uservalues.offeror_values.split()))[-1]
                    uservalues.save()
                    current_robot.save()
                    return render(request, 'accounts/model_form_upload.html', {
                        'form': form, 'setting': settings[offeror_val], 'name':names[int(request.session['image_id'])],
                    })

                if "link" in request.POST:
                    uservalues = UserValues.objects.get(user=request.user)
                    link = request.POST.get("link")
                    segemented_link = link.split("/")
                    image_ids = getFlickrIds()
                    try:
                        image_id = int(image_ids[segemented_link[5]])
                    except (KeyError, IndexError):
                        errorMsg = "We're sorry! The link doesn't exist! Are you sure you copied it correct from the album we specified? Please retry!"
                        form = DocumentForm()
                        return render(request, 'accounts/model_form_upload.html', {
                            'form': form, 'error': errorMsg
                        })
                    offeror_val = list(map(float, uservalues.offeror_values.split()))[-1]
                    imagePath = "images/" + str(imageId) + ".png"
                    return render(request, 'accounts/model_form_upload.html', {
                        'image_id': image_id, "imagePath": imagePath,
                        'form': form, 'setting': settings[offeror_val], 'name':names[int(request.session['image_id'])]
                    })

                if "shared" in request.POST:
                    current_robot = Robots.objects.get(id=request.session['current_robot'])
                    (robot, user) = Game.imagePreference(request, current_robot, 0)
                    user_acceptor_values = list(map(float, user.user_acceptor_values.split()))
                    user_offeror_values = list(map(float, user.user_offeror_values.split()))
                    user_acceptor_values.append(user_acceptor_values[-1])
                    user_offeror_values.append(user_offeror_values[-1])
                    user.user_acceptor_values = " ".join(map(str, user_acceptor_values))
                    user.user_offeror_values = " ".join(map(str, user_offeror_values))
                    user.save()
                    robot.save()
                    result = ""
                    if request.session['success'] == True:
                        result = "pass"
                    elif request.session['failure'] == True:
                        result = "fail"
                    return render(request, 'accounts/model_form_upload.html', {
                        'result': result, 'name':names[int(request.session['image_id'])]
                    })

                if 'change' in request.POST:
                    change = 'Yes'
                    user = UserValues.objects.get(user=request.user)
                    user_acceptor_values = list(map(float, user.user_acceptor_values.split()))
                    user_offeror_values = list(map(float, user.user_offeror_values.split()))
                    del user_offeror_values[-1]
                    user_acceptor_values.append(user_acceptor_values[-1])
                    user_offeror_values.append(float(request.POST.get('change')))
                    user.user_acceptor_values = " ".join(map(str, user_acceptor_values))
                    user.user_offeror_values = " ".join(map(str, user_offeror_values))
                    user.save()
                    return render(request, 'accounts/model_form_upload.html', {
                        'change': change,
                    })
        else:
            settings = getSettings()
            if imageId % 2 == 1:
                imagePath = "images/" + str(imageId) + ".png"
                args = {'image_id':imageId, 'imagePath':imagePath, 'text':getImageTexts()[str(imageId)],
                        'name': names[int(imageId-1)], 'setting': settings[request.session['robot_offeror_value']]}
                return render(request, 'accounts/pages.html', args)
            else:
                current_robot, uservalues = Game.getRobot(request, 0)
                request.session['current_robot'] = current_robot.id
                form = DocumentForm()
                offeror_val = list(map(float, uservalues.offeror_values.split()))[-1]
                uservalues.save()
                current_robot.save()
                return render(request, 'accounts/model_form_upload.html', {
                    'form': form, 'setting': settings[offeror_val], 'name':names[int(request.session['image_id'])],
                })
    else:
        return render(request, 'accounts/login.html')

@login_required()
def profile(request):
    if request.user.is_authenticated:
        uservalues = UserValues.objects.get(user=request.user)
        if 'image_id' not in request.session:
            request.session['image_id'] = uservalues.image_id
        imageId = request.session['image_id']

        if(imageId >= len(getImageTexts())):
            return render(request, 'accounts/finished.html', {'imageId':imageId})

        args = {'username': request.user.username, 'user':uservalues,
                'image_id':uservalues.image_id, 'firstLogin':uservalues.firstLogin,
                'offeror':'No', 'acceptor':'No'}

        if imageId % 2 == 0:
            args['toggle'] = 'upload'
        else:
            args['toggle'] = 'pages'

        if 'showQuestions' in request.POST:
            request.session['questions'] = 'Yes'
        if 'questions' in request.session:
            args['questions'] = request.session['questions']

        if 'offeror' in request.POST:
            offeror = request.POST.get('offeror')
            uservalues.comfort = float(offeror)
            uservalues.offeror_values = offeror
            uservalues.user_offeror_values = offeror
            request.session['offeror'] = 'Yes'
            uservalues.save()

        if 'acceptor' in request.POST:
            comfort = request.POST.get('acceptor')
            uservalues.comfort = float(comfort)
            request.session['acceptor']= 'Yes'
            uservalues.acceptor_values = comfort
            uservalues.user_acceptor_values = comfort
            uservalues.save()

        if 'offeror' in request.session:
            args['offeror'] = request.session['offeror']
        if 'acceptor' in request.session:
            args['acceptor'] = request.session['acceptor']

        return render(request, 'accounts/profile.html', args)


@login_required()
def logout(request):
    uservalues = UserValues.objects.get(user=request.user)
    if 'image_id' in request.session:
        uservalues.image_id = request.session['image_id']
    if 'robot_offeror_value' in request.session:
        uservalues.last_robot_value = request.session['robot_offeror_value']
    uservalues.save()
    request.session.flush()
    auth.logout(request)
    return render(request, "accounts/logout.html")