# Functions file
from django import http
from . import util

# Django Method
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# To Convert markdown file to a HTML file
from markdown2 import Markdown

# for random Function
import secrets

# for Forms classes
from django import forms


# for NewEntry-Page and Edit-check class
class NewEntry(forms.Form):
    title = forms.CharField(label="Entry title", widget=forms.TextInput(
        attrs={
            'class': 'form-control mb-4',
            'placeholder': 'Type In Yor Markdown content Title For Your Page.',
            'name': 'title',
        }
    ))
    content = forms.CharField(label="Entry content", widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Type In Yor Markdown content For Your Page',
            'row': 5,
        }
    ))

    # use to define if (submitvlaue-editvalue)
    edit = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(), required=False)


# for the Home page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# for all single entry-page
def entry(request, entry):
    markdowner = Markdown()
    # page content (.md);
    page = util.get_entry(entry)
    # if page is True, (if there is an entryPage);
    if page is None:
        return render(request, "encyclopedia/error.html", {"title": entry})

    # (if there isn't an entryPage) return errorPage;
    else:
        context = {
            # convert the page To htmlContent
            "entry": markdowner.convert(page),
            # changing the title
            "title": entry
        }
        return render(request, "encyclopedia/pages.html", context)


# for search function:
def search(request):
    # User-search-Result:
    searchResult = request.GET.get('q', None)

    # if the entry allready exist:
    if (util.get_entry(searchResult)):
        return HttpResponseRedirect(reverse('entry', kwargs={'entry': searchResult}))
    else:
        # empty list for the SearchResult
        subEntry = []
        for entry in util.list_entries():
            # check for case-sensitive
            if searchResult.upper() in entry.upper():
                subEntry.append(entry)
        # for Substring-Page
        context = {
            "entries": subEntry,
            # To change the Title(h1) with (if)
            "search": True
        }
        return render(request, 'encyclopedia/index.html', context)


# for creating newEntry
def newEntryPage(request):
    if request.method == "POST":
        # For saves user's entry;
        form = NewEntry(request.POST)

        # check validation
        if form.is_valid():
            entryTitle = form.cleaned_data['title']
            entryContent = form.cleaned_data['content']

            # check if the Entry Isn't EXIST and it isn't editing:
            if(util.get_entry(entryTitle) is None or form.cleaned_data['edit'] is True):
                # adding (title / content) to return them togather
                # save user's Entry
                util.save_entry(entryTitle, entryContent)
                return HttpResponseRedirect(reverse('entry', kwargs={'entry': entryTitle}))

            else:
                context = {
                    'existing': True,
                    # for changing the title (edit/create)
                    'entry': entryTitle,
                    'form': form
                }
                return render(request, "encyclopedia/newform.html", context)

    # The Default
    else:
        return render(request, 'encyclopedia/newform.html', {
            'form': NewEntry(),
            'existing': False
        })


# for edit Entry
def edit(request, entry):
    # Get Entry to Edit
    page = util.get_entry(entry)
    if page:
        # get the form for edit
        form = NewEntry()
        # fill the form with the existing content
        form.fields["title"].initial = entry  # the title
        form.fields["content"].initial = page  # the content
        # the user cann't edit the title inpust
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["edit"].initial = True  # for edit content

        return render(request, 'encyclopedia/newform.html', {
            'form': form,
            'edit': form.fields['edit'].initial,
            'title': form.fields['title'].initial
        })

    else:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })


# for Random Entries
def randomPage(request):
    entries = util.list_entries()
    randomChoice = secrets.choice(entries)
    return HttpResponseRedirect(reverse('entry', kwargs={'entry': randomChoice}))
