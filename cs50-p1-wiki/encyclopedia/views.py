import random

from django.shortcuts import render
from django import forms
from markdown2 import Markdown

from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Input content using the Markdown markup language'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    entry_content = util.get_entry(entry)
    if entry_content == None:
        return render(request, "encyclopedia/sorry.html")
    else:
        # Converts markdown content to HTML to proper visualization
        markdowner = Markdown()
        html_format = markdowner.convert(entry_content)

        return render(request, "encyclopedia/entry.html", {
            "entry": html_format,
            "title": entry.capitalize()
        })


def search(request):
    query = request.GET['q']
    entry_content = util.get_entry(query)
    if entry_content == None:
        entries_list = util.list_entries()
        found_results = []
        for entry in entries_list:
            if query.lower() in entry.lower():
                found_results.append(entry)
        return render(request, "encyclopedia/search-results.html", {
            "results": found_results
        })
    else:
        # Converts markdown content to HTML to proper visualization
        markdowner = Markdown()
        html_format = markdowner.convert(entry_content)

        return render(request, "encyclopedia/entry.html", {
            "entry": html_format,
            "title": query.capitalize()
        })


def new_page(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the data from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Prevent duplicate entries
            entries_list = util.list_entries()
            for entry in entries_list:
                if title.lower() in entry.lower():
                    return render(request, "encyclopedia/new-page.html", {
                        "message": f'Sorry, not possible. The title "{title}" already exists, please try again.',
                        "form": form
                    })
                
            # Save the new page/entry 
            util.save_entry(title, content)

            # Get the new page and displays it
            entry = util.get_entry(title)

            # Converts markdown content to HTML to proper visualization
            markdowner = Markdown()
            html_format = markdowner.convert(entry)

            return render(request, "encyclopedia/entry.html", {
                "entry": html_format,
                "title": title.capitalize()
            })

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/new-page.html", {
                "message": f'Sorry, not possible. Incorrect data, please try again.',
                "form": form
            })
    
    # Resquest method is GET
    else:
        return render(request, "encyclopedia/new-page.html", {
            "form": NewPageForm()
        })


def edit_page(request, title):
    if request.method == "POST":
        content = request.POST['content']
        
        util.save_entry(title, content)

        entry_content = util.get_entry(title)

        # Converts markdown content to HTML to proper visualization
        markdowner = Markdown()
        html_format = markdowner.convert(entry_content)

        return render(request, "encyclopedia/entry.html", {
                "entry": html_format,
                "title": title.capitalize()
            })
    else:
        entry_content = util.get_entry(title)
        if entry_content == None:
            return render(request, "encyclopedia/sorry.html")
        else:
            return render(request, "encyclopedia/edit-page.html", {
                "title": title,
                "content": entry_content
            })


def get_random(request):
    entries = util.list_entries()

    # get a random element from the entries list
    random_choice = random.choice(entries)

    entry_content = util.get_entry(random_choice)

    # Converts markdown content to HTML to proper visualization
    markdowner = Markdown()
    html_format = markdowner.convert(entry_content)

    return render(request, "encyclopedia/entry.html", {
        "entry": html_format,
        "title": random_choice.capitalize()
    })
    