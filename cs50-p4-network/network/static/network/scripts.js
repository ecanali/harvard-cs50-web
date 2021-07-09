// Listen to any clicks on Edit Post and Like Post
document.addEventListener('DOMContentLoaded', function() {
    editLinks = document.querySelectorAll('.edit-post');
    for (let link of editLinks) {
        link.addEventListener('click', (event) => editPost(event));
    }

    likeLinks = document.querySelectorAll('.like-post');
    for (let link of likeLinks) {
        link.addEventListener('click', (event) => likePost(event));
    }
});

function editPost(event) {
    // Prevent standard anchor behavior of making a request
    event.preventDefault();

    // Hide original text
    postDiv = document.getElementById(`${event.target.dataset.post}`);
    pTag = postDiv.getElementsByTagName('p')[0];
    pTag.style.display = 'none';

    // Disable edit link preventing multiple textarea
    editLink = postDiv.querySelector('.edit-post')
    editLink.classList.add('disabled');

    // Create a form to update the text
    const form = document.createElement('form');

    // Create a textarea with the original text inside
    const textArea = document.createElement('textarea');
    textArea.value = pTag.innerHTML;
    textArea.className = 'form-control';
    form.append(textArea);

    // Create button to submit the updated text
    const saveButton = document.createElement('input');
    saveButton.setAttribute('type', 'submit');
    saveButton.setAttribute('value', 'Save');
    saveButton.dataset.post = event.target.dataset.post;
    saveButton.className = 'btn btn-primary';
    form.append(saveButton);

    saveButton.onclick = (event) => { 
        // Prevent standard submit behavior of reloading the page
        event.preventDefault();

        // Save the new post text into database
        fetch(`/edit/${event.target.dataset.post}`, {
            method: 'PUT',
            body: JSON.stringify({
                content: textArea.value
            })
        });

        // Return the layout to the original with updated text
        form.style.display = 'none';
        pTag.innerHTML = textArea.value;
        pTag.style.display = 'block';
        editLink.classList.remove('disabled');
    }

    // Add the textarea form in the place of the post text
    pTag.parentNode.insertBefore(form, pTag.nextSibling);
}

function likePost(event) {
    // Prevent standard anchor behavior of making a request
    event.preventDefault();

    // Save the new like/unlike into database
    fetch(`/like/${event.target.dataset.post}`);
    
    // Update the like icon preparation
    postDiv = document.getElementById(`${event.target.dataset.post}`);
    icon = postDiv.querySelector('.material-icons');

    // Update the like counter preparation
    counter = postDiv.querySelector('.counter');
    num_counter = parseInt(counter.innerHTML);

    // Update the link text, icon and counter accordingly
    if (event.target.innerHTML == 'Like') {
        event.target.innerHTML = 'Unlike';
        icon.innerHTML = 'favorite';
        counter.innerHTML = num_counter + 1;
    } else {
        event.target.innerHTML = 'Like';
        icon.innerHTML = 'favorite_border';
        counter.innerHTML = num_counter - 1;
    }
}
